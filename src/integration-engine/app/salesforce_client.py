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

    def to_cypher(self, sobject: str, fields: List[str], filter_clause: Optional[str] = None, sort_field: Optional[str] = None, sort_order: str = "DESC", limit: int = 50) -> str:
        """Converts sObject query parameters into openCypher/Neo4j query syntax"""
        var_name = sobject[0].lower()
        fields_str = ", ".join([f"{var_name}.{f.strip()}" for f in fields if f.strip()])
        cypher = f"MATCH ({var_name}:{sobject})"
        if filter_clause and filter_clause.strip():
            clause = filter_clause.strip()
            import re
            for f in ["Type", "Industry", "Name", "AnnualRevenue", "BillingCity", "Phone", "LastModifiedDate"]:
                clause = re.sub(rf"\b{f}\b", f"{var_name}.{f}", clause)
            cypher += f" WHERE {clause}"
        cypher += f" RETURN {fields_str}"
        if sort_field and sort_field.strip():
            cypher += f" ORDER BY {var_name}.{sort_field.strip()} {sort_order}"
        cypher += f" LIMIT {limit}"
        return cypher

    async def get_records(
        self, 
        sobject: str, 
        access_token: str, 
        instance_url: str,
        search: Optional[str] = None,
        media_only: Optional[bool] = False
    ) -> List[Dict[str, Any]]:
        """Fetch records from live Salesforce Org via SOQL query using user credentials, supporting media filters and search"""
        fields_map = {
            "Account": "Id, Name, Type, Industry, AnnualRevenue, Phone, BillingCity, BillingCountry, CreatedDate, LastModifiedDate",
            "Contact": "Id, FirstName, LastName, Email, Title, AccountId, Account.Name, Phone, CreatedDate, LastModifiedDate",
            "Opportunity": "Id, Name, StageName, Amount, CloseDate, Probability, AccountId, Account.Name, CreatedDate, LastModifiedDate",
            "Lead": "Id, FirstName, LastName, Company, Email, Status, Phone, CreatedDate, LastModifiedDate"
        }
        fields = fields_map.get(sobject, "Id, Name, CreatedDate, LastModifiedDate")
        fields_list = [f.strip() for f in fields.split(",") if f.strip()]
        var_name = sobject[0].lower()

        where_clauses = []
        cypher_where_clauses = []
        self.last_llm_telemetry = None

        # Check if query is media_only or NLP query
        from .nlp_query_service import nlp_service
        if media_only:
            nlp_res = nlp_service.parse_nlp_query("all media", context_sobject=sobject)
            self.last_nlp_interpretation = nlp_res["interpretation"]
            self.last_llm_telemetry = nlp_res.get("llm_telemetry")
            soql = nlp_res["soql"]
            cypher = nlp_res["cypher"]
        elif search and search.strip():
            nlp_res = nlp_service.parse_nlp_query(search.strip(), context_sobject=sobject)
            self.last_nlp_interpretation = nlp_res["interpretation"]
            self.last_llm_telemetry = nlp_res.get("llm_telemetry")
            soql = nlp_res["soql"]
            cypher = nlp_res["cypher"]
        else:
            soql = f"SELECT {fields} FROM {sobject} ORDER BY LastModifiedDate DESC LIMIT 50"
            fields_cypher = ", ".join([f"{var_name}.{f}" for f in fields_list])
            cypher = f"MATCH ({var_name}:{sobject}) RETURN {fields_cypher} ORDER BY {var_name}.LastModifiedDate DESC LIMIT 50"
            self.last_nlp_interpretation = {
                "entity": sobject,
                "is_media_query": False,
                "notes": [f"Retrieved recent {sobject} records"],
                "summary": f"Target: {sobject} ➔ Default recent records"
            }
            self.last_llm_telemetry = {
                "engine": "Internal Local LLM",
                "model": "Internal-CRM-LLM-v1",
                "inference_time_ms": 0.1,
                "tokens_processed": 0,
                "confidence_score": 1.0,
                "slots_extracted": {},
                "reasoning_chain": [f"Default recent {sobject} projection"]
            }

        self.last_soql_query = soql
        self.last_cypher_query = cypher

        try:
            return await self.query(soql, access_token=access_token, instance_url=instance_url)
        except Exception as e:
            # Fallback to direct REST endpoint if query fails and no search/media filter applied
            if not (media_only or (search and search.strip())):
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

    async def describe_sobject(self, sobject: str, access_token: str, instance_url: str) -> Dict[str, Any]:
        """Fetch full sObject field metadata from Salesforce Describe API"""
        headers = self._get_headers(access_token)
        url = f"{instance_url.rstrip('/')}/services/data/{self.api_version}/sobjects/{sobject}/describe"
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                fields = [
                    {
                        "name": f.get("name"),
                        "label": f.get("label"),
                        "type": f.get("type"),
                        "custom": f.get("custom", False),
                        "nillable": f.get("nillable", True),
                        "calculated": f.get("calculated", False)
                    }
                    for f in data.get("fields", [])
                ]
                return {
                    "name": data.get("name"),
                    "label": data.get("label"),
                    "keyPrefix": data.get("keyPrefix"),
                    "fields": fields
                }
            raise Exception(f"Salesforce describe failed ({resp.status_code}): {resp.text}")

sf_client = SalesforceClient()
