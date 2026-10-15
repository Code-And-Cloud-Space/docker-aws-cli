import re
from typing import Dict, List, Optional, Tuple, Any

class SchemaLinker:
    """
    Schema Linking and CRM Ontology Engine.
    Maps unstructured natural language tokens to exact Salesforce sObjects,
    child-to-parent relationship traversal paths (dot-notation), and property graph edge schemas.
    """

    DEFAULT_FIELDS = {
        "Account": "Id, Name, Type, Industry, AnnualRevenue, Phone, BillingCity, BillingCountry, CreatedDate, LastModifiedDate",
        "Contact": "Id, FirstName, LastName, Email, Title, AccountId, Account.Name, Phone, CreatedDate, LastModifiedDate",
        "Opportunity": "Id, Name, StageName, Amount, CloseDate, Probability, AccountId, Account.Name, CreatedDate, LastModifiedDate",
        "Lead": "Id, FirstName, LastName, Company, Email, Status, Phone, CreatedDate, LastModifiedDate"
    }

    RELATIONSHIPS = {
        "Contact": {
            "parent": "Account",
            "foreign_key": "AccountId",
            "soql_prefix": "Account",
            "cypher_edge": "BELONGS_TO"
        },
        "Opportunity": {
            "parent": "Account",
            "foreign_key": "AccountId",
            "soql_prefix": "Account",
            "cypher_edge": "BELONGS_TO"
        }
    }

    JOB_KEYWORDS = {
        "vp": ["VP", "Vice President"],
        "vice president": ["Vice President", "VP"],
        "director": ["Director"],
        "manager": ["Manager"],
        "lead": ["Lead", "Principal"],
        "head": ["Head of", "Head"],
        "officer": ["Officer", "Chief"],
        "executive": ["Executive", "Officer"],
        "c-level": ["CEO", "CTO", "CFO", "COO", "CIO"],
        "engineer": ["Engineer", "Developer", "Architect"],
        "sales": ["Sales", "Account Executive", "Business Development"],
        "marketing": ["Marketing", "Growth"]
    }

    INDUSTRY_KEYWORDS = [
        "media", "technology", "tech", "consulting", "banking",
        "finance", "healthcare", "energy", "hospitality",
        "manufacturing", "retail"
    ]

    def extract_relationship_account(self, text: str, entity: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extracts specific parent Account entity name for Contact or Opportunity queries
        while preventing generic industry or stage keywords from masquerading as company names.
        """
        if entity not in ["Contact", "Opportunity"]:
            return None, None

        job_blacklist = set(self.JOB_KEYWORDS.keys()) | {
            "person", "people", "employee", "employees", "staff", "deal", "deals",
            "opportunity", "opportunities", "closed won", "closed lost", "closed",
            "won", "lost", "pipeline", "high value", "high revenue", "recent",
            "new", "top", "active", "open", "all", "qualified", "media related",
            "media", "media type", "media industry", "technology related", "tech related"
        }
        filter_phrases = ["closed won", "closed lost", "high value", "high revenue", "recent", "open deals", "pipeline"]

        # Pattern 1: "<Account> person/deal" e.g. "Get Global Media person"
        m1 = re.search(r'\b(?:get|find|show|search|list|fetch)?\s*(?:all\s*)?(?:the\s*)?([A-Za-z0-9\s&]+?)\s+(?:person|people|employee|employees|staff|team member|worker|contacts?|deals?|opportunities?)\b', text, re.IGNORECASE)
        if m1:
            raw_cand = re.sub(r'^(?:get|find|show|search|list|fetch|all|the|any|a|an)\s+', '', m1.group(1).strip(), flags=re.IGNORECASE).strip()
            candidate = re.sub(r'\s+(?:related|associated|connected)(?:\s+to)?$', '', raw_cand, flags=re.IGNORECASE).strip()
            cand_lower = candidate.lower()
            if candidate and cand_lower not in job_blacklist and not any(fp in cand_lower for fp in filter_phrases) and len(candidate) > 1:
                if cand_lower not in ["media", "tech", "technology"]:
                    return candidate, f"Slot 'Account.Name' extracted from pre-entity position: '{candidate}'"

        # Pattern 2: "person/contact/deal (at|for|from|with) <Account>"
        m2 = re.search(r'\b(?:contacts?|people|person|employees?|staff|deals?|opportunities?)\s+(?:at|for|from|in|of|under|with account|with company|in account)\s+[\"\'\s]?([A-Za-z0-9\s&]+?)[\"\'\s]?(?:\s+(?:with|who|and|where)\b.*|$)', text, re.IGNORECASE)
        if m2:
            raw_cand = re.sub(r'^(?:the|any|a|an)\s+', '', m2.group(1).strip(), flags=re.IGNORECASE).strip()
            candidate = re.sub(r'\s+(?:related|associated|connected)(?:\s+to)?$', '', raw_cand, flags=re.IGNORECASE).strip()
            cand_lower = candidate.lower()
            if candidate and cand_lower not in job_blacklist and not any(fp in cand_lower for fp in filter_phrases) and len(candidate) > 1:
                if cand_lower not in ["media", "tech", "technology"]:
                    return candidate, f"Slot 'Account.Name' extracted from prepositional phrase: '{candidate}'"

        return None, None
