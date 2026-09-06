import json
import boto3
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from . import config

class LocalSecretsManager:
    """
    Replicated AWS Secrets Manager client.
    Stores sensitive credentials (Salesforce Client Secrets, Refresh Tokens)
    in AWS Secrets Manager (LocalStack or AWS Cloud) with local fallback.
    """
    def __init__(self):
        kwargs = {
            "region_name": config.AWS_REGION,
            "aws_access_key_id": config.AWS_ACCESS_KEY_ID,
            "aws_secret_access_key": config.AWS_SECRET_ACCESS_KEY,
        }
        if config.AWS_ENDPOINT_URL:
            kwargs["endpoint_url"] = config.AWS_ENDPOINT_URL

        self.client = boto3.client("secretsmanager", **kwargs)
        self._local_cache: Dict[str, str] = {}

    def put_secret(self, secret_name: str, secret_value: Dict[str, Any], description: str = "") -> str:
        """Create or update a secret in Secrets Manager"""
        secret_string = json.dumps(secret_value)
        try:
            try:
                # Try creating new secret
                resp = self.client.create_secret(
                    Name=secret_name,
                    SecretString=secret_string,
                    Description=description
                )
                return resp.get("ARN", f"arn:aws:secretsmanager:{config.AWS_REGION}:000000000000:secret:{secret_name}")
            except self.client.exceptions.ResourceExistsException:
                # Update existing secret
                resp = self.client.put_secret_value(
                    SecretId=secret_name,
                    SecretString=secret_string
                )
                return resp.get("ARN", f"arn:aws:secretsmanager:{config.AWS_REGION}:000000000000:secret:{secret_name}")
        except Exception as e:
            # Local fallback cache in case SecretsManager service is starting
            print(f"[SecretsManager] AWS Secrets Manager notice ({e}), caching locally for {secret_name}")
            self._local_cache[secret_name] = secret_string
            return f"local-secret-arn:{secret_name}"

    def get_secret(self, secret_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve and parse a secret from Secrets Manager"""
        try:
            resp = self.client.get_secret_value(SecretId=secret_name)
            secret_str = resp.get("SecretString", "{}")
            return json.loads(secret_str)
        except Exception as e:
            if secret_name in self._local_cache:
                return json.loads(self._local_cache[secret_name])
            return None

    def delete_secret(self, secret_name: str) -> bool:
        """Delete secret immediately without recovery window"""
        try:
            self.client.delete_secret(SecretId=secret_name, ForceDeleteWithoutRecovery=True)
            if secret_name in self._local_cache:
                del self._local_cache[secret_name]
            return True
        except Exception:
            if secret_name in self._local_cache:
                del self._local_cache[secret_name]
                return True
            return False

    def list_secrets_metadata(self) -> list:
        """List metadata for all managed secrets"""
        try:
            resp = self.client.list_secrets()
            return [
                {
                    "name": s["Name"],
                    "arn": s.get("ARN"),
                    "description": s.get("Description"),
                    "lastChangedDate": s.get("LastChangedDate", datetime.now(timezone.utc)).isoformat() if hasattr(s.get("LastChangedDate"), "isoformat") else str(s.get("LastChangedDate"))
                }
                for s in resp.get("SecretList", [])
            ]
        except Exception:
            return [
                {"name": k, "arn": f"local-secret-arn:{k}", "description": "Local cached secret"}
                for k in self._local_cache.keys()
            ]

secrets_manager = LocalSecretsManager()
