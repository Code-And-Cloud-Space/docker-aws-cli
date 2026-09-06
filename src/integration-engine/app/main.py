import json
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Depends, Query, Header, BackgroundTasks
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from . import config
from .database import (
    get_db,
    init_db,
    SalesforceOAuthToken,
    SalesforceAccount,
    SalesforceContact,
    SalesforceOpportunity
)
from .secrets_manager import secrets_manager
from .oauth_service import oauth_service
from .aws_client import aws_manager
from .salesforce_client import sf_client
from .sync_service import (
    full_sync_salesforce_to_aws,
    sync_single_salesforce_record,
    handle_salesforce_cdc_event,
    push_aws_event_to_salesforce,
    upsert_crm_record_to_mysql,
    log_sync_event,
    SYNC_LOGS
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize MySQL schema on startup
    init_db()
    yield

app = FastAPI(
    title="Salesforce <-> AWS Integration Engine",
    description="Live Salesforce OAuth 2.0 PKCE Engine with Session Isolation, Secrets Manager & MySQL CRM Tables",
    version="2.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------------------
# Request / Response Schemas & Helpers
# ------------------------------------------------------------------------------
def get_session_id(
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    session_id: Optional[str] = Query(None)
) -> Optional[str]:
    """Extracts session ID from HTTP header X-Session-ID or query parameter session_id"""
    val = x_session_id or session_id
    if not val or val.strip() == "" or val == "null" or val == "undefined":
        return None
    return val.strip()

def require_authenticated_salesforce_session(
    session_id: Optional[str] = Depends(get_session_id),
    db: Session = Depends(get_db)
) -> SalesforceOAuthToken:
    """
    Strict security guard: Ensures an active, valid Salesforce OAuth connection exists for this session.
    If not connected or invalid, raises 401 Unauthorized so no data is exposed.
    """
    if not session_id:
        raise HTTPException(
            status_code=401,
            detail="Authentication required: No Salesforce session found. Please connect to Salesforce via OAuth."
        )
    token_rec = db.query(SalesforceOAuthToken).filter(
        SalesforceOAuthToken.session_id == session_id,
        SalesforceOAuthToken.is_active == True
    ).order_by(SalesforceOAuthToken.id.desc()).first()
    if not token_rec:
        raise HTTPException(
            status_code=401,
            detail="Authentication required: No active Salesforce connection found for this session. Please connect via OAuth."
        )
    return token_rec

class SyncRecordPayload(BaseModel):
    sobject: str
    record_id: str
    session_id: Optional[str] = None

class AWSToSalesforcePayload(BaseModel):
    sobject: str
    record_id: Optional[str] = None
    data: Dict[str, Any]

# ------------------------------------------------------------------------------
# Root & System Status
# ------------------------------------------------------------------------------
@app.get("/")
def root():
    return {
        "service": "Salesforce <-> AWS Integration Engine",
        "auth_flow": "OAuth 2.0 Authorization Code with PKCE (S256)",
        "aws_endpoint": config.AWS_ENDPOINT_URL,
        "mysql_database": config.MYSQL_DATABASE,
        "status": "online"
    }

@app.get("/api/status")
async def get_system_status(
    session_id: Optional[str] = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    aws_health = aws_manager.check_health()
    
    token_rec = None
    if session_id:
        token_rec = db.query(SalesforceOAuthToken).filter(
            SalesforceOAuthToken.session_id == session_id,
            SalesforceOAuthToken.is_active == True
        ).order_by(SalesforceOAuthToken.id.desc()).first()

    sf_status = "disconnected"
    sf_details = {}

    if token_rec:
        now = datetime.now(timezone.utc)
        token_exp = token_rec.expires_at.replace(tzinfo=timezone.utc) if token_rec.expires_at.tzinfo is None else token_rec.expires_at
        is_expired = now >= token_exp
        seconds_left = max(0, int((token_exp - now).total_seconds()))

        sf_status = "expired" if is_expired else "connected"
        sf_details = {
            "sessionId": token_rec.session_id,
            "instanceUrl": token_rec.instance_url,
            "salesforceOrgId": token_rec.salesforce_org_id,
            "salesforceUserId": token_rec.salesforce_user_id,
            "salesforceUsername": token_rec.salesforce_username,
            "issuedAt": token_rec.issued_at.isoformat() if token_rec.issued_at else None,
            "expiresAt": token_rec.expires_at.isoformat() if token_rec.expires_at else None,
            "expiresInSeconds": seconds_left,
            "isExpired": is_expired,
            "secretArn": token_rec.refresh_token_secret_arn,
            "lastRefreshedAt": token_rec.last_refreshed_at.isoformat() if token_rec.last_refreshed_at else None
        }

    return {
        "sessionId": session_id,
        "salesforce": {
            "status": sf_status,
            **sf_details
        },
        "aws": {
            "status": "connected" if any(aws_health.values()) else "error",
            "services": aws_health,
            "region": config.AWS_REGION,
            "endpoint": config.AWS_ENDPOINT_URL
        },
        "recentLogsCount": len(SYNC_LOGS) if sf_status in ("connected", "expired") else 0
    }

# ------------------------------------------------------------------------------
# Salesforce OAuth 2.0 Authorization Code Flow Endpoints
# ------------------------------------------------------------------------------
@app.get("/api/auth/salesforce/login")
def get_salesforce_login_url(
    custom_login_url: Optional[str] = Query(None),
    session_id: Optional[str] = Depends(get_session_id)
):
    """Generates the OAuth2 Authorization URL with PKCE (S256) and browser session_id"""
    if not config.SALESFORCE_CLIENT_ID:
        raise HTTPException(
            status_code=400,
            detail="SALESFORCE_CLIENT_ID is not configured in .env. Please set up your Connected App."
        )
    auth_url = oauth_service.get_authorization_url(custom_login_url=custom_login_url, session_id=session_id)
    return {"authUrl": auth_url, "sessionId": session_id, "redirectUri": config.SALESFORCE_REDIRECT_URI}

@app.get("/api/auth/salesforce/callback")
async def salesforce_oauth_callback(
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    error_description: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Salesforce redirects back to this Callback URL with ?code=...&state=...
    Exchanges authorization code with PKCE verification for tokens,
    stores refresh token in Secrets Manager, and records token metadata & expiration in MySQL per session.
    """
    if error:
        error_msg = f"Salesforce OAuth Error: {error} - {error_description}"
        return RedirectResponse(url=f"{config.FRONTEND_REDIRECT_URL}?auth_error={error_msg}")

    if not code:
        return RedirectResponse(url=f"{config.FRONTEND_REDIRECT_URL}?auth_error=No authorization code received")

    code_verifier = None
    session_id = None

    if state:
        try:
            state_dict = json.loads(state)
            state_id = state_dict.get("sid")
            session_id = state_dict.get("sess")

            # Retrieve code_verifier from memory store or fallback state payload
            from .oauth_service import PKCE_SESSIONS
            if state_id and state_id in PKCE_SESSIONS:
                sess_info = PKCE_SESSIONS.pop(state_id)
                code_verifier = sess_info.get("code_verifier")
                if not session_id:
                    session_id = sess_info.get("session_id")
            elif "cv" in state_dict:
                code_verifier = state_dict["cv"]
        except Exception:
            pass

    try:
        result = await oauth_service.exchange_code(
            code=code,
            db=db,
            code_verifier=code_verifier,
            session_id=session_id
        )
        return RedirectResponse(
            url=f"{config.FRONTEND_REDIRECT_URL}?auth_success=true&session_id={session_id or ''}&instance_url={result['instanceUrl']}"
        )
    except Exception as e:
        return RedirectResponse(url=f"{config.FRONTEND_REDIRECT_URL}?auth_error={str(e)}")

@app.post("/api/auth/salesforce/refresh")
async def refresh_salesforce_token(
    session_id: Optional[str] = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """Explicitly test token rotation using refresh token from AWS Secrets Manager for current session"""
    if not session_id:
        raise HTTPException(status_code=401, detail="No active session found to refresh.")
    try:
        new_token, instance_url = await oauth_service.refresh_active_token(db=db, session_id=session_id)
        return {
            "status": "success",
            "message": "Token refreshed successfully via Secrets Manager",
            "sessionId": session_id,
            "instanceUrl": instance_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/salesforce/disconnect")
def disconnect_salesforce(
    session_id: Optional[str] = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """Revokes active token in MySQL and deletes refresh token from AWS Secrets Manager for this session"""
    if not session_id:
        raise HTTPException(status_code=400, detail="No session ID provided to disconnect.")
    oauth_service.disconnect(db=db, session_id=session_id)
    return {"status": "success", "message": "Salesforce disconnected successfully", "sessionId": session_id}

# ------------------------------------------------------------------------------
# Secrets Manager Inspection Endpoint
# ------------------------------------------------------------------------------
@app.get("/api/secrets")
def list_managed_secrets(_auth: SalesforceOAuthToken = Depends(require_authenticated_salesforce_session)):
    """Lists metadata for all secrets stored in local/cloud AWS Secrets Manager (requires active Salesforce connection)"""
    return {"secrets": secrets_manager.list_secrets_metadata()}

# ------------------------------------------------------------------------------
# Live Salesforce Data & Sync Endpoints
# ------------------------------------------------------------------------------
@app.get("/api/salesforce/records/{sobject}")
async def get_salesforce_records(
    sobject: str,
    session_id: Optional[str] = Depends(get_session_id),
    db: Session = Depends(get_db),
    _auth: SalesforceOAuthToken = Depends(require_authenticated_salesforce_session)
):
    try:
        access_token, instance_url = await oauth_service.get_valid_token(db, session_id=session_id)
        records = await sf_client.get_records(sobject, access_token=access_token, instance_url=instance_url)
        return {"sobject": sobject, "totalSize": len(records), "records": records, "instanceUrl": instance_url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401 if "No active Salesforce session" in str(e) else 500, detail=str(e))

@app.post("/api/salesforce/records/{sobject}")
async def create_salesforce_record(
    sobject: str,
    payload: Dict[str, Any],
    session_id: Optional[str] = Depends(get_session_id),
    db: Session = Depends(get_db),
    _auth: SalesforceOAuthToken = Depends(require_authenticated_salesforce_session)
):
    try:
        access_token, instance_url = await oauth_service.get_valid_token(db, session_id=session_id)
        res = await sf_client.create_record(sobject, payload, access_token=access_token, instance_url=instance_url)
        record_id = res.get("id")

        # Auto mirror in MySQL, DynamoDB & S3
        if record_id:
            full_rec = await sf_client.get_record(sobject, record_id, access_token=access_token, instance_url=instance_url)
            if full_rec:
                upsert_crm_record_to_mysql(sobject, full_rec)
                aws_manager.upsert_sync_record(
                    sobject_type=sobject,
                    salesforce_id=record_id,
                    payload=full_rec,
                    sync_status="SYNCED"
                )
                aws_manager.upload_raw_event(
                    event_id=f"created-{sobject}-{record_id}",
                    data=full_rec
                )

        log_sync_event(
            event_type=f"SALESFORCE_CREATE_{sobject}",
            status="SUCCESS",
            details={"sobject": sobject, "recordId": record_id, "payload": payload, "sessionId": session_id}
        )
        return {"id": record_id, "success": True, "result": res}
    except HTTPException:
        raise
    except Exception as e:
        log_sync_event(
            event_type=f"SALESFORCE_CREATE_{sobject}",
            status="ERROR",
            details={"error": str(e), "payload": payload, "sessionId": session_id}
        )
        raise HTTPException(status_code=401 if "No active Salesforce session" in str(e) else 500, detail=str(e))

# ------------------------------------------------------------------------------
# Single Record Sync Endpoint ("Sync to AWS & DB" button)
# ------------------------------------------------------------------------------
@app.post("/api/sync/record")
async def sync_single_record(
    payload: SyncRecordPayload,
    session_id: Optional[str] = Depends(get_session_id),
    db: Session = Depends(get_db),
    _auth: SalesforceOAuthToken = Depends(require_authenticated_salesforce_session)
):
    """Syncs a single record from Salesforce into MySQL, DynamoDB, and S3"""
    active_sess = payload.session_id or session_id
    try:
        access_token, instance_url = await oauth_service.get_valid_token(db, session_id=active_sess)
        result = await sync_single_salesforce_record(
            sobject=payload.sobject,
            record_id=payload.record_id,
            access_token=access_token,
            instance_url=instance_url
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401 if "No active Salesforce session" in str(e) else 500, detail=str(e))

# ------------------------------------------------------------------------------
# MySQL Local Database CRM Tables Inspection Endpoints
# ------------------------------------------------------------------------------
@app.get("/api/db/accounts")
def get_db_accounts(
    limit: int = 100,
    db: Session = Depends(get_db),
    _auth: SalesforceOAuthToken = Depends(require_authenticated_salesforce_session)
):
    accounts = db.query(SalesforceAccount).order_by(SalesforceAccount.id.desc()).limit(limit).all()
    formatted = [
        {
            "id": a.id,
            "salesforceId": a.salesforce_id,
            "name": a.name,
            "type": a.type,
            "industry": a.industry,
            "phone": a.phone,
            "website": a.website,
            "annualRevenue": a.annual_revenue,
            "syncStatus": a.sync_status,
            "createdAt": a.created_at.isoformat() if a.created_at else None,
            "updatedAt": a.updated_at.isoformat() if a.updated_at else None
        }
        for a in accounts
    ]
    return {
        "total": len(accounts),
        "records": formatted,
        "accounts": formatted
    }

@app.get("/api/db/contacts")
def get_db_contacts(
    limit: int = 100,
    db: Session = Depends(get_db),
    _auth: SalesforceOAuthToken = Depends(require_authenticated_salesforce_session)
):
    contacts = db.query(SalesforceContact).order_by(SalesforceContact.id.desc()).limit(limit).all()
    formatted = [
        {
            "id": c.id,
            "salesforceId": c.salesforce_id,
            "accountId": c.account_id,
            "accountSalesforceId": c.account_salesforce_id,
            "name": c.name or f"{c.first_name or ''} {c.last_name or ''}".strip(),
            "firstName": c.first_name,
            "lastName": c.last_name,
            "email": c.email,
            "phone": c.phone,
            "title": c.title,
            "department": c.department,
            "syncStatus": c.sync_status,
            "createdAt": c.created_at.isoformat() if c.created_at else None,
            "updatedAt": c.updated_at.isoformat() if c.updated_at else None
        }
        for c in contacts
    ]
    return {
        "total": len(contacts),
        "records": formatted,
        "contacts": formatted
    }

@app.get("/api/db/opportunities")
def get_db_opportunities(
    limit: int = 100,
    db: Session = Depends(get_db),
    _auth: SalesforceOAuthToken = Depends(require_authenticated_salesforce_session)
):
    opps = db.query(SalesforceOpportunity).order_by(SalesforceOpportunity.id.desc()).limit(limit).all()
    formatted = [
        {
            "id": o.id,
            "salesforceId": o.salesforce_id,
            "accountId": o.account_id,
            "accountSalesforceId": o.account_salesforce_id,
            "name": o.name,
            "stageName": o.stage_name,
            "amount": o.amount,
            "probability": o.probability,
            "closeDate": o.close_date.isoformat() if o.close_date else None,
            "type": o.type,
            "syncStatus": o.sync_status,
            "createdAt": o.created_at.isoformat() if o.created_at else None,
            "updatedAt": o.updated_at.isoformat() if o.updated_at else None
        }
        for o in opps
    ]
    return {
        "total": len(opps),
        "records": formatted,
        "opportunities": formatted
    }

@app.post("/api/sync/salesforce-to-aws")
async def trigger_full_sync(
    session_id: Optional[str] = Depends(get_session_id),
    db: Session = Depends(get_db),
    _auth: SalesforceOAuthToken = Depends(require_authenticated_salesforce_session)
):
    try:
        access_token, instance_url = await oauth_service.get_valid_token(db, session_id=session_id)
        result = await full_sync_salesforce_to_aws(access_token=access_token, instance_url=instance_url)
        return {"status": "success", "summary": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401 if "No active Salesforce session" in str(e) else 500, detail=str(e))

@app.post("/api/sync/aws-to-salesforce")
async def trigger_aws_to_sf(
    payload: AWSToSalesforcePayload,
    session_id: Optional[str] = Depends(get_session_id),
    db: Session = Depends(get_db),
    _auth: SalesforceOAuthToken = Depends(require_authenticated_salesforce_session)
):
    try:
        access_token, instance_url = await oauth_service.get_valid_token(db, session_id=session_id)
        result = await push_aws_event_to_salesforce(
            sobject=payload.sobject,
            payload=payload.data,
            access_token=access_token,
            instance_url=instance_url,
            record_id=payload.record_id
        )
        return {"status": "success", "result": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401 if "No active Salesforce session" in str(e) else 500, detail=str(e))

@app.post("/api/webhook/salesforce-cdc")
async def salesforce_cdc_webhook(event: Dict[str, Any], background_tasks: BackgroundTasks):
    result = await handle_salesforce_cdc_event(event)
    return result

# ------------------------------------------------------------------------------
# AWS Resource Inspection Endpoints
# ------------------------------------------------------------------------------
@app.get("/api/aws/dynamodb/records")
def get_dynamodb_records(
    _auth: SalesforceOAuthToken = Depends(require_authenticated_salesforce_session)
):
    records = aws_manager.get_all_dynamodb_records()
    return {"total": len(records), "records": records}

@app.get("/api/aws/s3/files")
def get_s3_files(
    bucket: Optional[str] = None,
    _auth: SalesforceOAuthToken = Depends(require_authenticated_salesforce_session)
):
    target_bucket = bucket or config.S3_RAW_EVENTS_BUCKET
    files = aws_manager.list_s3_files(bucket=target_bucket)
    return {"bucket": target_bucket, "totalFiles": len(files), "files": files}

@app.get("/api/aws/s3/file")
def get_s3_file(
    key: str = Query(...),
    bucket: Optional[str] = None,
    _auth: SalesforceOAuthToken = Depends(require_authenticated_salesforce_session)
):
    target_bucket = bucket or config.S3_RAW_EVENTS_BUCKET
    try:
        return aws_manager.get_s3_file_content(key=key, bucket=target_bucket)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/aws/sqs/stats")
def get_sqs_stats(
    _auth: SalesforceOAuthToken = Depends(require_authenticated_salesforce_session)
):
    return aws_manager.get_sqs_stats()

@app.get("/api/logs")
def get_sync_logs(
    limit: int = 50,
    _auth: SalesforceOAuthToken = Depends(require_authenticated_salesforce_session)
):
    return {"logs": SYNC_LOGS[:limit]}
