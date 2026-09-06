import httpx
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from . import config

class SalesforceClient:
    def __init__(self):
        self.api_version: str = config.SALESFORCE_API_VERSION

    def _get_headers(self, access_token: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    async def get_records(self, sobject: str, access_token: str, instance_url: str) -> List[Dict[str, Any]]:
        """Fetch records from live Salesforce Org via SOQL query using user credentials"""
        fields_map = {
            "Account": "Id, Name, Type, Industry, AnnualRevenue, Phone, BillingCity, BillingCountry, CreatedDate, LastModifiedDate",
            "Contact": "Id, FirstName, LastName, Email, Title, AccountId, Phone, CreatedDate, LastModifiedDate",
            "Opportunity": "Id, Name, StageName, Amount, CloseDate, Probability, AccountId, CreatedDate, LastModifiedDate",
            "Lead": "Id, FirstName, LastName, Company, Email, Status, Phone, CreatedDate, LastModifiedDate"
        }
        fields = fields_map.get(sobject, "Id, Name, CreatedDate, LastModifiedDate")
        soql = f"SELECT {fields} FROM {sobject} ORDER BY LastModifiedDate DESC LIMIT 50"

        try:
            return await self.query(soql, access_token=access_token, instance_url=instance_url)
        except Exception as e:
            # Fallback to direct REST endpoint if SOQL query fails
            headers = self._get_headers(access_token)
            url = f"{instance_url.rstrip('/')}/services/data/{self.api_version}/sobjects/{sobject}"
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    return resp.json().get("records", [])
                raise e

    async def get_record(self, sobject: str, record_id: str, access_token: str, instance_url: str) -> Optional[Dict[str, Any]]:
        headers = self._get_headers(access_token)
        url = f"{instance_url.rstrip('/')}/services/data/{self.api_version}/sobjects/{sobject}/{record_id}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                return resp.json()
            return None

    async def create_record(self, sobject: str, payload: Dict[str, Any], access_token: str, instance_url: str) -> Dict[str, Any]:
        headers = self._get_headers(access_token)
        url = f"{instance_url.rstrip('/')}/services/data/{self.api_version}/sobjects/{sobject}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code in [200, 201]:
                return resp.json()
            raise Exception(f"Salesforce create failed ({resp.status_code}): {resp.text}")

    async def update_record(self, sobject: str, record_id: str, payload: Dict[str, Any], access_token: str, instance_url: str) -> Dict[str, Any]:
        headers = self._get_headers(access_token)
        url = f"{instance_url.rstrip('/')}/services/data/{self.api_version}/sobjects/{sobject}/{record_id}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.patch(url, headers=headers, json=payload)
            if resp.status_code in [200, 204]:
                return {"id": record_id, "success": True}
            raise Exception(f"Salesforce update failed ({resp.status_code}): {resp.text}")

    async def delete_record(self, sobject: str, record_id: str, access_token: str, instance_url: str) -> bool:
        headers = self._get_headers(access_token)
        url = f"{instance_url.rstrip('/')}/services/data/{self.api_version}/sobjects/{sobject}/{record_id}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.delete(url, headers=headers)
            return resp.status_code in [200, 204]

    async def query(self, soql: str, access_token: str, instance_url: str) -> List[Dict[str, Any]]:
        headers = self._get_headers(access_token)
        url = f"{instance_url.rstrip('/')}/services/data/{self.api_version}/query"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=headers, params={"q": soql})
            if resp.status_code == 200:
                data = resp.json()
                return data.get("records", [])
            raise Exception(f"Salesforce SOQL failed ({resp.status_code}): {resp.text}")

sf_client = SalesforceClient()
