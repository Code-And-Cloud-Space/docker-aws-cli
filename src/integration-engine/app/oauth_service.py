import base64
import hashlib
import json
import secrets
import urllib.parse
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Tuple
import httpx
from sqlalchemy.orm import Session

from . import config
from .database import SalesforceOAuthToken
from .secrets_manager import secrets_manager
from .sync_service import log_sync_event

# In-memory store for PKCE verifiers keyed by state session ID
# Format: { state_key: {"code_verifier": verifier, "session_id": session_id, "created_at": timestamp} }
PKCE_SESSIONS: Dict[str, Dict[str, Any]] = {}

def generate_pkce_pair() -> Tuple[str, str]:
    """
    Generates a cryptographically secure PKCE code_verifier and code_challenge (S256).
    RFC 7636 compliant for Salesforce OAuth 2.0 PKCE.
    """
    code_verifier = secrets.token_urlsafe(64)
    hashed = hashlib.sha256(code_verifier.encode("ascii")).digest()
    code_challenge = base64.urlsafe_b64encode(hashed).decode("ascii").rstrip("=")
    return code_verifier, code_challenge

class SalesforceOAuthService:
    def get_authorization_url(
        self,
        custom_login_url: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> str:
        """Constructs Salesforce OAuth 2.0 Authorization URL with PKCE (S256) and browser session_id"""
        login_base = (custom_login_url or config.SALESFORCE_LOGIN_URL or "https://login.salesforce.com").rstrip("/")
        
        # Generate PKCE verifier and challenge
        code_verifier, code_challenge = generate_pkce_pair()
        state_id = secrets.token_urlsafe(16)
        now_ts = datetime.now(timezone.utc).timestamp()

        # Clean up stale PKCE sessions older than 10 minutes
        stale_keys = [k for k, v in PKCE_SESSIONS.items() if now_ts - v.get("created_at", 0) > 600]
        for k in stale_keys:
            PKCE_SESSIONS.pop(k, None)

        # Store in PKCE sessions memory store
        PKCE_SESSIONS[state_id] = {
            "code_verifier": code_verifier,
            "session_id": session_id,
            "created_at": now_ts
        }

        # Embed state_id, session_id, and fallback code_verifier in state payload
        state_payload = json.dumps({
            "sid": state_id,
            "sess": session_id,
            "cv": code_verifier,
            "ts": now_ts
        })

        params = {
            "response_type": "code",
            "client_id": config.SALESFORCE_CLIENT_ID,
            "redirect_uri": config.SALESFORCE_REDIRECT_URI,
            "scope": config.SALESFORCE_SCOPES,
            "state": state_payload,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256"
        }
        return f"{login_base}/services/oauth2/authorize?{urllib.parse.urlencode(params)}"

    async def exchange_code(
        self,
        code: str,
        db: Session,
        code_verifier: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Exchanges Authorization Code for Access & Refresh Tokens and persists to Secrets Manager + MySQL per session"""
        token_endpoint = f"{config.SALESFORCE_LOGIN_URL.rstrip('/')}/services/oauth2/token"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": config.SALESFORCE_CLIENT_ID,
            "client_secret": config.SALESFORCE_CLIENT_SECRET,
            "redirect_uri": config.SALESFORCE_REDIRECT_URI,
        }
        if code_verifier:
            data["code_verifier"] = code_verifier

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(token_endpoint, data=data)
            if resp.status_code != 200:
                error_detail = f"OAuth Code exchange failed ({resp.status_code}): {resp.text}"
                log_sync_event("OAUTH_AUTH_CODE_ERROR", "ERROR", {"error": resp.text})
                raise Exception(error_detail)

            token_data = resp.json()

        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        if not refresh_token:
            print("[OAuthService] WARNING: Salesforce token response did not include a refresh_token. Verify that 'refresh_token' / 'offline_access' scope is assigned to your Connected App.")
        instance_url = token_data.get("instance_url")
        id_url = token_data.get("id", "")
        
        # Parse user ID and org ID from id url
        id_parts = id_url.rstrip("/").split("/")
        sf_org_id = id_parts[-2] if len(id_parts) >= 2 else None
        sf_user_id = id_parts[-1] if len(id_parts) >= 1 else None

        # Fetch Salesforce user details from identity endpoint
        sf_username = None
        if id_url and access_token:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    id_resp = await client.get(id_url, headers={"Authorization": f"Bearer {access_token}"})
                    if id_resp.status_code == 200:
                        id_json = id_resp.json()
                        sf_username = id_json.get("username") or id_json.get("display_name")
            except Exception as e:
                print(f"[OAuthService] Could not fetch identity info: {e}")

        # Calculate expiration
        expires_in = int(token_data.get("expires_in", 7200))
        now_utc = datetime.now(timezone.utc)
        expires_at = now_utc + timedelta(seconds=expires_in)

        # 1. Store Refresh Token in AWS Secrets Manager keyed by session or active
        secret_name = f"salesforce/{session_id or 'active_connection'}/refresh_token"
        secret_arn = secrets_manager.put_secret(
            secret_name=secret_name,
            secret_value={
                "sessionId": session_id,
                "salesforceUserId": sf_user_id,
                "salesforceOrgId": sf_org_id,
                "salesforceUsername": sf_username,
                "refreshToken": refresh_token,
                "clientId": config.SALESFORCE_CLIENT_ID,
                "instanceUrl": instance_url,
                "savedAt": now_utc.isoformat()
            },
            description=f"Salesforce OAuth2 Refresh Token for Session {session_id or 'Active'}"
        )

        # 2. Deactivate previous active tokens for this session
        if session_id:
            db.query(SalesforceOAuthToken).filter(
                SalesforceOAuthToken.session_id == session_id,
                SalesforceOAuthToken.is_active == True
            ).update({"is_active": False})
        else:
            db.query(SalesforceOAuthToken).filter(
                SalesforceOAuthToken.is_active == True
            ).update({"is_active": False})

        # 3. Save new active Token Record in MySQL
        token_record = SalesforceOAuthToken(
            session_id=session_id,
            salesforce_user_id=sf_user_id,
            salesforce_org_id=sf_org_id,
            salesforce_username=sf_username,
            instance_url=instance_url,
            access_token=access_token,
            refresh_token_secret_arn=secret_arn,
            token_type=token_data.get("token_type", "Bearer"),
            issued_at=now_utc,
            expires_at=expires_at,
            is_active=True
        )
        db.add(token_record)
        db.commit()
        db.refresh(token_record)

        log_sync_event("OAUTH_LOGIN_SUCCESS", "SUCCESS", {
            "sessionId": session_id,
            "salesforceUserId": sf_user_id,
            "salesforceOrgId": sf_org_id,
            "salesforceUsername": sf_username,
            "instanceUrl": instance_url,
            "expiresAt": expires_at.isoformat(),
            "secretArn": secret_arn
        })

        return {
            "sessionId": session_id,
            "instanceUrl": instance_url,
            "salesforceOrgId": sf_org_id,
            "salesforceUserId": sf_user_id,
            "salesforceUsername": sf_username,
            "expiresAt": expires_at.isoformat(),
            "secretArn": secret_arn
        }

    async def get_valid_token(self, db: Session, session_id: Optional[str] = None) -> Tuple[str, str]:
        """
        Retrieves a valid access token and instance URL for the specified session_id.
        If no session_id is provided or token is not active for this session, raises exception.
        If access token is near expiry (< 60s), rotates token via Secrets Manager.
        """
        if not session_id:
            raise Exception("No active Salesforce session found for this browser. Please connect via OAuth.")

        token_record = db.query(SalesforceOAuthToken).filter(
            SalesforceOAuthToken.session_id == session_id,
            SalesforceOAuthToken.is_active == True
        ).order_by(SalesforceOAuthToken.id.desc()).first()

        if not token_record:
            raise Exception("No active Salesforce session found for this browser. Please connect via OAuth.")

        now_utc = datetime.now(timezone.utc)
        token_expires_at = token_record.expires_at.replace(tzinfo=timezone.utc) if token_record.expires_at.tzinfo is None else token_record.expires_at

        if now_utc >= (token_expires_at - timedelta(seconds=60)):
            print(f"[OAuthService] Token for session {session_id} is expired or expiring at {token_expires_at}. Refreshing...")
            return await self.refresh_active_token(db, session_id=session_id)

        return token_record.access_token, token_record.instance_url

    async def refresh_active_token(self, db: Session, session_id: Optional[str] = None) -> Tuple[str, str]:
        """Refreshes expired access token using refresh_token stored in Secrets Manager"""
        if not session_id:
            raise Exception("No session_id provided to refresh active token.")

        token_record = db.query(SalesforceOAuthToken).filter(
            SalesforceOAuthToken.session_id == session_id,
            SalesforceOAuthToken.is_active == True
        ).order_by(SalesforceOAuthToken.id.desc()).first()

        if not token_record:
            raise Exception("No active token record found for this session to refresh.")

        # Retrieve secret using full ARN or fallback to session secret name
        secret_id = token_record.refresh_token_secret_arn
        secret_data = secrets_manager.get_secret(secret_id) if secret_id else None
        
        if not secret_data or not secret_data.get("refreshToken"):
            # Fallback to friendly secret name
            fallback_name = f"salesforce/{session_id}/refresh_token"
            secret_data = secrets_manager.get_secret(fallback_name)

        if not secret_data or not secret_data.get("refreshToken"):
            raise Exception("No refresh token found in Secrets Manager. Please re-authenticate.")

        refresh_token = secret_data["refreshToken"]
        token_endpoint = f"{config.SALESFORCE_LOGIN_URL.rstrip('/')}/services/oauth2/token"

        data = {
            "grant_type": "refresh_token",
            "client_id": config.SALESFORCE_CLIENT_ID,
            "client_secret": config.SALESFORCE_CLIENT_SECRET,
            "refresh_token": refresh_token
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(token_endpoint, data=data)
            if resp.status_code != 200:
                error_msg = f"Failed to refresh Salesforce token ({resp.status_code}): {resp.text}"
                log_sync_event("OAUTH_REFRESH_ERROR", "ERROR", {"error": resp.text})
                raise Exception(error_msg)

            refreshed_data = resp.json()

        new_access_token = refreshed_data.get("access_token")
        instance_url = refreshed_data.get("instance_url") or secret_data.get("instanceUrl")
        expires_in = int(refreshed_data.get("expires_in", 7200))
        now_utc = datetime.now(timezone.utc)
        new_expires_at = now_utc + timedelta(seconds=expires_in)

        # Update MySQL token record
        token_record.access_token = new_access_token
        token_record.instance_url = instance_url
        token_record.expires_at = new_expires_at
        token_record.last_refreshed_at = now_utc
        db.commit()
        db.refresh(token_record)

        log_sync_event("OAUTH_TOKEN_REFRESHED", "SUCCESS", {
            "sessionId": session_id,
            "newExpiresAt": new_expires_at.isoformat(),
            "instanceUrl": instance_url
        })

        return new_access_token, instance_url

    def disconnect(self, db: Session, session_id: Optional[str] = None):
        """Revokes active connection and removes secrets for session"""
        query = db.query(SalesforceOAuthToken).filter(SalesforceOAuthToken.is_active == True)
        if session_id:
            query = query.filter(SalesforceOAuthToken.session_id == session_id)

        tokens = query.all()
        for t in tokens:
            t.is_active = False
            try:
                secret_id = t.refresh_token_secret_arn or f"salesforce/{t.session_id or 'active_connection'}/refresh_token"
                secrets_manager.delete_secret(secret_id)
            except Exception:
                pass

        db.commit()
        log_sync_event("OAUTH_DISCONNECTED", "SUCCESS", {"sessionId": session_id})

oauth_service = SalesforceOAuthService()
