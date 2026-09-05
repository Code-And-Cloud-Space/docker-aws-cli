import httpx
from typing import Dict, Any, List, Optional
from . import config

class SalesforceClient:
    def __init__(self):
        self.instance_url: str = config.SALESFORCE_INSTANCE_URL.rstrip("/") if config.SALESFORCE_INSTANCE_URL else ""
        self.access_token: Optional[str] = config.SALESFORCE_ACCESS_TOKEN or None
        self.api_version: str = config.SALESFORCE_API_VERSION

    async def authenticate(self) -> str:
        """Authenticate directly against live Salesforce Org"""
        # If pre-configured access token exists, use it directly
        if config.SALESFORCE_ACCESS_TOKEN and config.SALESFORCE_INSTANCE_URL:
            self.access_token = config.SALESFORCE_ACCESS_TOKEN
            self.instance_url = config.SALESFORCE_INSTANCE_URL.rstrip("/")
            return self.access_token

        login_url = (config.SALESFORCE_LOGIN_URL or "https://login.salesforce.com").rstrip("/")
        token_endpoint = f"{login_url}/services/oauth2/token"

        auth_type = config.SALESFORCE_AUTH_TYPE

        if auth_type == "oauth_password":
            # Username-Password flow with optional security token
            password_full = f"{config.SALESFORCE_PASSWORD}{config.SALESFORCE_SECURITY_TOKEN}"
            data = {
                "grant_type": "password",
                "client_id": config.SALESFORCE_CLIENT_ID,
                "client_secret": config.SALESFORCE_CLIENT_SECRET,
                "username": config.SALESFORCE_USERNAME,
                "password": password_full,
            }
        else:
            # Client credentials flow
            data = {
                "grant_type": "client_credentials",
                "client_id": config.SALESFORCE_CLIENT_ID,
                "client_secret": config.SALESFORCE_CLIENT_SECRET,
            }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(token_endpoint, data=data)
            if resp.status_code == 200:
                payload = resp.json()
                self.access_token = payload.get("access_token")
                # Capture real instance_url (e.g. https://yourcompany.my.salesforce.com)
                if payload.get("instance_url"):
                    self.instance_url = payload["instance_url"].rstrip("/")
                elif not self.instance_url:
                    self.instance_url = login_url
                return self.access_token
            else:
                error_msg = f"Live Salesforce Auth failed ({resp.status_code}): {resp.text}"
                print(f"[SalesforceClient] {error_msg}")
                raise Exception(error_msg)

    async def get_headers(self) -> Dict[str, str]:
        if not self.access_token or not self.instance_url:
            await self.authenticate()
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    async def get_records(self, sobject: str) -> List[Dict[str, Any]]:
        """Fetch records from live Salesforce Org via SOQL query"""
        fields_map = {
            "Account": "Id, Name, Type, Industry, AnnualRevenue, Phone, BillingCity, BillingCountry, CreatedDate, LastModifiedDate",
            "Contact": "Id, FirstName, LastName, Email, Title, AccountId, Phone, CreatedDate, LastModifiedDate",
            "Opportunity": "Id, Name, StageName, Amount, CloseDate, Probability, AccountId, CreatedDate, LastModifiedDate",
            "Lead": "Id, FirstName, LastName, Company, Email, Status, Phone, CreatedDate, LastModifiedDate"
        }
        fields = fields_map.get(sobject, "Id, Name, CreatedDate, LastModifiedDate")
        soql = f"SELECT {fields} FROM {sobject} ORDER BY LastModifiedDate DESC LIMIT 50"

        try:
            return await self.query(soql)
        except Exception as e:
            # Fallback to direct REST endpoint if SOQL query fails
            headers = await self.get_headers()
            url = f"{self.instance_url}/services/data/{self.api_version}/sobjects/{sobject}"
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    return resp.json().get("records", [])
                raise e

    async def get_record(self, sobject: str, record_id: str) -> Optional[Dict[str, Any]]:
        headers = await self.get_headers()
        url = f"{self.instance_url}/services/data/{self.api_version}/sobjects/{sobject}/{record_id}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                return resp.json()
            return None

    async def create_record(self, sobject: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        headers = await self.get_headers()
        url = f"{self.instance_url}/services/data/{self.api_version}/sobjects/{sobject}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code in [200, 201]:
                return resp.json()
            raise Exception(f"Salesforce create failed ({resp.status_code}): {resp.text}")

    async def update_record(self, sobject: str, record_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        headers = await self.get_headers()
        url = f"{self.instance_url}/services/data/{self.api_version}/sobjects/{sobject}/{record_id}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.patch(url, headers=headers, json=payload)
            if resp.status_code in [200, 204]:
                return {"id": record_id, "success": True}
            raise Exception(f"Salesforce update failed ({resp.status_code}): {resp.text}")

    async def delete_record(self, sobject: str, record_id: str) -> bool:
        headers = await self.get_headers()
        url = f"{self.instance_url}/services/data/{self.api_version}/sobjects/{sobject}/{record_id}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.delete(url, headers=headers)
            return resp.status_code in [200, 204]

    async def query(self, soql: str) -> List[Dict[str, Any]]:
        headers = await self.get_headers()
        url = f"{self.instance_url}/services/data/{self.api_version}/query"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=headers, params={"q": soql})
            if resp.status_code == 200:
                data = resp.json()
                return data.get("records", [])
            raise Exception(f"Salesforce SOQL failed ({resp.status_code}): {resp.text}")

sf_client = SalesforceClient()
