import re
from typing import Dict, Any, List, Optional

class NLPQueryService:
    """
    Multi-Object Natural Language Processing (NLP) Query Engine for Salesforce & Graph Databases.
    Translates natural language requests across Account, Contact, Opportunity, Lead, etc.
    into optimized Salesforce SOQL and openCypher/Neo4j graph queries.
    """

    DEFAULT_FIELDS = {
        "Account": "Id, Name, Type, Industry, AnnualRevenue, Phone, BillingCity, BillingCountry, CreatedDate, LastModifiedDate",
        "Contact": "Id, FirstName, LastName, Email, Title, AccountId, Phone, CreatedDate, LastModifiedDate",
        "Opportunity": "Id, Name, StageName, Amount, CloseDate, Probability, AccountId, CreatedDate, LastModifiedDate",
        "Lead": "Id, FirstName, LastName, Company, Email, Status, Phone, CreatedDate, LastModifiedDate"
    }

    def parse_nlp_query(self, query_text: str, context_sobject: Optional[str] = None, default_limit: int = 50) -> Dict[str, Any]:
        """
        Parses an NLP query string for any sObject into entity, filters, SOQL, Cypher, and human-readable explanation.
        """
        text = query_text.strip()
        lower = text.lower()

        # ----------------------------------------------------------------------
        # 1. Detect Target sObject Entity
        # ----------------------------------------------------------------------
        sobject = None

        if any(w in lower for w in ["contact", "contacts", "people", "person", "employee", "employees"]):
            sobject = "Contact"
        elif any(w in lower for w in ["opportunity", "opportunities", "deal", "deals", "pipeline", "revenue deal"]):
            sobject = "Opportunity"
        elif any(w in lower for w in ["lead", "leads", "prospect", "prospects"]):
            sobject = "Lead"
        elif any(w in lower for w in ["account", "accounts", "company", "companies", "client", "clients", "customer", "customers", "vendor", "vendors"]):
            sobject = "Account"

        # Fallback to current context sObject if not explicitly mentioned in prompt
        if not sobject:
            sobject = context_sobject if context_sobject in self.DEFAULT_FIELDS else "Account"

        fields_str = self.DEFAULT_FIELDS.get(sobject, "Id, Name, CreatedDate, LastModifiedDate")
        fields_list = [f.strip() for f in fields_str.split(",") if f.strip()]
        var_name = sobject[0].lower()

        where_soql_clauses = []
        where_cypher_clauses = []
        filters_applied = []
        interpretation_notes = []

        # ----------------------------------------------------------------------
        # 2. Extract Custom Limit if specified (e.g. "top 10", "limit 25", "first 5")
        # ----------------------------------------------------------------------
        limit = default_limit
        limit_match = re.search(r'\b(?:limit|top|first)\s+(\d+)\b', lower)
        if limit_match:
            limit = min(max(1, int(limit_match.group(1))), 200)
            interpretation_notes.append(f"Limit set to {limit} records")

        # ----------------------------------------------------------------------
        # 3. Object-Specific NLP Extraction
        # ----------------------------------------------------------------------

        # === ACCOUNT ===
        if sobject == "Account":
            # Media pattern
            if bool(re.search(r'\bmedia\b', lower)):
                where_soql_clauses.append("(Type = 'Media' OR Industry = 'Media' OR Type LIKE '%Media%' OR Industry LIKE '%Media%' OR Name LIKE '%Media%')")
                where_cypher_clauses.append(f"({var_name}.Type = 'Media' OR {var_name}.Industry = 'Media' OR toLower({var_name}.Type) CONTAINS 'media' OR toLower({var_name}.Industry) CONTAINS 'media' OR toLower({var_name}.Name) CONTAINS 'media')")
                filters_applied.append("Type = 'Media' OR Industry = 'Media'")
                interpretation_notes.append("Identified criteria: Account Type or Industry matches 'Media'")
            
            # Other industries
            elif any(ind in lower for ind in ["technology", "tech", "consulting", "banking", "finance", "healthcare", "energy", "hospitality", "manufacturing", "retail", "education"]):
                for ind in ["technology", "consulting", "banking", "finance", "healthcare", "energy", "hospitality", "manufacturing", "retail", "education"]:
                    if ind in lower or (ind == "technology" and "tech" in lower):
                        val = "Technology" if ind in ["technology", "tech"] else ind.capitalize()
                        where_soql_clauses.append(f"(Industry = '{val}' OR Type = '{val}')")
                        where_cypher_clauses.append(f"({var_name}.Industry = '{val}' OR {var_name}.Type = '{val}')")
                        filters_applied.append(f"Industry/Type = '{val}'")
                        interpretation_notes.append(f"Identified industry filter: '{val}'")
                        break

            # Revenue extraction
            amount_match = re.search(r'(?:revenue|annualrevenue)\s*(?:>=|>|over|greater than|more than)\s*\$?([\d,]+)(k|m)?\b', lower)
            if amount_match:
                raw_num = amount_match.group(1).replace(",", "")
                multiplier = 1000 if amount_match.group(2) == 'k' else (1000000 if amount_match.group(2) == 'm' else 1)
                rev_val = float(raw_num) * multiplier
                where_soql_clauses.append(f"AnnualRevenue >= {rev_val}")
                where_cypher_clauses.append(f"{var_name}.AnnualRevenue >= {rev_val}")
                filters_applied.append(f"AnnualRevenue >= ${rev_val:,.0f}")
                interpretation_notes.append(f"Revenue criteria: AnnualRevenue >= ${rev_val:,.0f}")
            elif "high revenue" in lower or "enterprise" in lower or "vip" in lower:
                where_soql_clauses.append("AnnualRevenue >= 1000000")
                where_cypher_clauses.append(f"{var_name}.AnnualRevenue >= 1000000")
                filters_applied.append("AnnualRevenue >= $1,000,000")
                interpretation_notes.append("Filtered for high enterprise revenue (AnnualRevenue >= $1M)")

            # Rating
            if "hot" in lower:
                where_soql_clauses.append("Rating = 'Hot'")
                where_cypher_clauses.append(f"{var_name}.Rating = 'Hot'")
                filters_applied.append("Rating = 'Hot'")
                interpretation_notes.append("Filtered for Hot rated accounts")

        # === CONTACT ===
        elif sobject == "Contact":
            # Job Titles / Executive roles
            titles = []
            if "vp" in lower or "vice president" in lower:
                titles.extend(["VP", "Vice President"])
            if "director" in lower:
                titles.append("Director")
            if "manager" in lower:
                titles.append("Manager")
            if "ceo" in lower or "cfo" in lower or "cto" in lower or "executive" in lower:
                titles.extend(["Chief", "Officer", "Executive"])
            if "engineer" in lower or "developer" in lower:
                titles.extend(["Engineer", "Developer"])
            if "sales" in lower:
                titles.append("Sales")
            if "marketing" in lower:
                titles.append("Marketing")

            if titles:
                title_clauses = " OR ".join([f"Title LIKE '%{t}%'" for t in titles])
                where_soql_clauses.append(f"({title_clauses})")
                cypher_title = " OR ".join([f"toLower({var_name}.Title) CONTAINS '{t.lower()}'" for t in titles])
                where_cypher_clauses.append(f"({cypher_title})")
                filters_applied.append(f"Title matching: {', '.join(titles)}")
                interpretation_notes.append(f"Filtered for Contact Job Titles matching: {', '.join(titles)}")

            # Email constraints
            if "gmail" in lower:
                where_soql_clauses.append("Email LIKE '%@gmail.com'")
                where_cypher_clauses.append(f"toLower({var_name}.Email) CONTAINS '@gmail.com'")
                filters_applied.append("Email is Gmail")
                interpretation_notes.append("Filtered for Gmail email addresses")
            elif "with email" in lower or "has email" in lower:
                where_soql_clauses.append("(Email != null AND Email LIKE '%@%')")
                where_cypher_clauses.append(f"{var_name}.Email IS NOT NULL")
                filters_applied.append("Has valid Email")
                interpretation_notes.append("Filtered for contacts with valid email")

            # Phone constraints
            if "with phone" in lower or "has phone" in lower:
                where_soql_clauses.append("Phone != null")
                where_cypher_clauses.append(f"{var_name}.Phone IS NOT NULL")
                filters_applied.append("Has Phone")
                interpretation_notes.append("Filtered for contacts with phone numbers")

            # Media contacts
            if "media" in lower:
                where_soql_clauses.append("(Title LIKE '%Media%' OR Email LIKE '%media%')")
                where_cypher_clauses.append(f"(toLower({var_name}.Title) CONTAINS 'media' OR toLower({var_name}.Email) CONTAINS 'media')")
                filters_applied.append("Media Related Contact")
                interpretation_notes.append("Filtered for Media-related contact roles")

        # === OPPORTUNITY ===
        elif sobject == "Opportunity":
            # Stage names
            if "closed won" in lower or "won deals" in lower or "won" in lower:
                where_soql_clauses.append("StageName = 'Closed Won'")
                where_cypher_clauses.append(f"{var_name}.StageName = 'Closed Won'")
                filters_applied.append("StageName = 'Closed Won'")
                interpretation_notes.append("Filtered for Closed Won opportunities")
            elif "closed lost" in lower or "lost deals" in lower:
                where_soql_clauses.append("StageName = 'Closed Lost'")
                where_cypher_clauses.append(f"{var_name}.StageName = 'Closed Lost'")
                filters_applied.append("StageName = 'Closed Lost'")
                interpretation_notes.append("Filtered for Closed Lost opportunities")
            elif "prospecting" in lower:
                where_soql_clauses.append("StageName = 'Prospecting'")
                where_cypher_clauses.append(f"{var_name}.StageName = 'Prospecting'")
                filters_applied.append("StageName = 'Prospecting'")
                interpretation_notes.append("Filtered for Prospecting stage")
            elif "open" in lower or "active" in lower or "pipeline" in lower:
                where_soql_clauses.append("StageName NOT IN ('Closed Won', 'Closed Lost')")
                where_cypher_clauses.append(f"NOT {var_name}.StageName IN ['Closed Won', 'Closed Lost']")
                filters_applied.append("Active Pipeline (Open)")
                interpretation_notes.append("Filtered for active, open deals in pipeline")

            # Deal amount extraction
            amt_match = re.search(r'(?:amount|value|deal|worth)\s*(?:>=|>|over|greater than|more than)\s*\$?([\d,]+)(k|m)?\b', lower)
            if amt_match:
                raw_num = amt_match.group(1).replace(",", "")
                multiplier = 1000 if amt_match.group(2) == 'k' else (1000000 if amt_match.group(2) == 'm' else 1)
                deal_val = float(raw_num) * multiplier
                where_soql_clauses.append(f"Amount >= {deal_val}")
                where_cypher_clauses.append(f"{var_name}.Amount >= {deal_val}")
                filters_applied.append(f"Amount >= ${deal_val:,.0f}")
                interpretation_notes.append(f"Filtered for deal value Amount >= ${deal_val:,.0f}")
            elif "high value" in lower or "big deals" in lower:
                where_soql_clauses.append("Amount >= 50000")
                where_cypher_clauses.append(f"{var_name}.Amount >= 50000")
                filters_applied.append("Amount >= $50,000")
                interpretation_notes.append("Filtered for high-value deals (Amount >= $50,000)")

            # Probability
            if "high probability" in lower or "likely" in lower:
                where_soql_clauses.append("Probability >= 70")
                where_cypher_clauses.append(f"{var_name}.Probability >= 70")
                filters_applied.append("Probability >= 70%")
                interpretation_notes.append("Filtered for high probability deals (>= 70%)")

            # Media deals
            if "media" in lower:
                where_soql_clauses.append("Name LIKE '%Media%'")
                where_cypher_clauses.append(f"toLower({var_name}.Name) CONTAINS 'media'")
                filters_applied.append("Media Deals")
                interpretation_notes.append("Filtered for Media industry opportunities")

        # === LEAD ===
        elif sobject == "Lead":
            if "qualified" in lower:
                where_soql_clauses.append("Status LIKE '%Qualified%'")
                where_cypher_clauses.append(f"toLower({var_name}.Status) CONTAINS 'qualified'")
                filters_applied.append("Status is Qualified")
                interpretation_notes.append("Filtered for Qualified leads")
            elif "open" in lower:
                where_soql_clauses.append("Status = 'Open - Not Contacted'")
                where_cypher_clauses.append(f"{var_name}.Status = 'Open - Not Contacted'")
                filters_applied.append("Status = 'Open - Not Contacted'")
                interpretation_notes.append("Filtered for Open leads")
            elif "working" in lower or "contacted" in lower:
                where_soql_clauses.append("Status = 'Working - Contacted'")
                where_cypher_clauses.append(f"{var_name}.Status = 'Working - Contacted'")
                filters_applied.append("Status = 'Working - Contacted'")
                interpretation_notes.append("Filtered for Working / Contacted leads")

            if "media" in lower:
                where_soql_clauses.append("(Company LIKE '%Media%' OR Industry = 'Media')")
                where_cypher_clauses.append(f"(toLower({var_name}.Company) CONTAINS 'media' OR {var_name}.Industry = 'Media')")
                filters_applied.append("Media Leads")
                interpretation_notes.append("Filtered for Media industry leads")

        # ----------------------------------------------------------------------
        # 4. Fallback Keyword Search if no structured rules triggered
        # ----------------------------------------------------------------------
        cleaned_search = re.sub(
            r'\b(search|find|show|get|list|all|the|of|with|type|records?|accounts?|contacts?|opportunities?|deals?|leads?)\b', 
            '', 
            lower
        ).strip()

        if not filters_applied and cleaned_search:
            clean_val = cleaned_search.replace("'", "\\'")
            if sobject in ["Contact", "Lead"]:
                where_soql_clauses.append(f"(FirstName LIKE '%{clean_val}%' OR LastName LIKE '%{clean_val}%' OR Email LIKE '%{clean_val}%')")
                where_cypher_clauses.append(f"(toLower({var_name}.FirstName) CONTAINS '{clean_val}' OR toLower({var_name}.LastName) CONTAINS '{clean_val}' OR toLower({var_name}.Email) CONTAINS '{clean_val}')")
            elif sobject == "Opportunity":
                where_soql_clauses.append(f"(Name LIKE '%{clean_val}%' OR StageName LIKE '%{clean_val}%')")
                where_cypher_clauses.append(f"(toLower({var_name}.Name) CONTAINS '{clean_val}' OR toLower({var_name}.StageName) CONTAINS '{clean_val}')")
            else:
                where_soql_clauses.append(f"(Name LIKE '%{clean_val}%' OR Industry LIKE '%{clean_val}%' OR Type LIKE '%{clean_val}%')")
                where_cypher_clauses.append(f"(toLower({var_name}.Name) CONTAINS '{clean_val}' OR toLower({var_name}.Industry) CONTAINS '{clean_val}')")

            filters_applied.append(f"Keyword '{cleaned_search}'")
            interpretation_notes.append(f"Keyword search applied across fields for: '{cleaned_search}'")

        # ----------------------------------------------------------------------
        # 5. Construct Final SOQL & openCypher Queries
        # ----------------------------------------------------------------------
        where_soql_str = f" WHERE {' AND '.join(where_soql_clauses)}" if where_soql_clauses else ""
        soql = f"SELECT {fields_str} FROM {sobject}{where_soql_str} ORDER BY LastModifiedDate DESC LIMIT {limit}"

        where_cypher_str = f" WHERE {' AND '.join(where_cypher_clauses)}" if where_cypher_clauses else ""
        cypher_fields = ", ".join([f"{var_name}.{f}" for f in fields_list])
        cypher = f"MATCH ({var_name}:{sobject}){where_cypher_str} RETURN {cypher_fields} ORDER BY {var_name}.LastModifiedDate DESC LIMIT {limit}"

        explanation = "; ".join(interpretation_notes) if interpretation_notes else f"Retrieved all recent {sobject} records"

        return {
            "raw_query": query_text,
            "sobject": sobject,
            "filters_applied": filters_applied,
            "soql": soql,
            "cypher": cypher,
            "limit": limit,
            "interpretation": {
                "entity": sobject,
                "is_media_query": "media" in lower,
                "notes": interpretation_notes,
                "summary": f"Target: {sobject} ➔ {explanation}"
            }
        }

nlp_service = NLPQueryService()
