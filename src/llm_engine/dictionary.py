import os
import re
import json
import urllib.request
import urllib.parse
from typing import Dict, Any, List, Optional
from datetime import datetime

DICTIONARY_PATH = os.path.join(os.path.dirname(__file__), "crm_dictionary.json")

class CRMDictionary:
    """
    Pure Semantic CRM Ontology & Knowledge Base.
    
    Contains ONLY term details, concepts, descriptions, and entity metadata:
    - Entity synonyms (e.g. 'company' -> Account, 'deal' -> Opportunity, 'pipeline' -> Opportunity)
    - Lifecycle concept definitions (e.g. 'open pipeline' -> active_open_pipeline, field: IsClosed = False)
    - Pure entity query recognition (e.g. 'company' inquiries)
    - Autonomous web learning: Discovers semantic concepts from online resources
      and indexes semantic metadata into crm_dictionary.json with ZERO query syntax.
    
    All dialect query synthesis (SOQL/openCypher) is performed by the LLM & QuerySynthesizer.
    """

    def __init__(self, dict_path: str = DICTIONARY_PATH):
        self.dict_path = dict_path
        self.data: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Loads semantic dictionary data from JSON file."""
        if os.path.exists(self.dict_path):
            try:
                with open(self.dict_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                    return
            except Exception as e:
                print(f"[CRMDictionary] Warning: Failed to load {self.dict_path}: {e}")

        # Fallback default knowledge base
        self.data = {
            "version": "2.0.0",
            "entities": {
                "Account": {
                    "synonyms": ["account", "accounts", "company", "companies", "firm", "firms", "business", "organization", "client", "vendor", "partner"],
                    "description": "Business organizations, client companies, and partner accounts."
                },
                "Opportunity": {
                    "synonyms": ["opportunity", "opportunities", "deal", "deals", "opp", "opps", "pipeline", "pipelines", "sale", "sales", "bid"],
                    "description": "Sales deals, revenue opportunities, and active pipeline transactions."
                },
                "Contact": {
                    "synonyms": ["contact", "contacts", "person", "people", "individual", "employee", "staff", "executive"],
                    "description": "Individuals and people associated with accounts and opportunities."
                },
                "Lead": {
                    "synonyms": ["lead", "leads", "prospect", "prospects", "inquiry", "inquiries"],
                    "description": "Unqualified prospects, potential leads, and inbound inquiries."
                }
            },
            "lifecycle_terms": {},
            "learned_terms": {}
        }

    def save(self) -> None:
        """Persists semantic dictionary to JSON file."""
        try:
            self.data["last_updated"] = datetime.utcnow().isoformat() + "Z"
            with open(self.dict_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"[CRMDictionary] Error saving {self.dict_path}: {e}")

    def get_entity_synonyms(self) -> Dict[str, List[str]]:
        """Returns entity synonyms dictionary."""
        syns = {}
        for ent, info in self.data.get("entities", {}).items():
            syns[ent] = info.get("synonyms", [])
        return syns

    def resolve_lifecycle_concept(self, entity: str, text: str) -> Optional[Dict[str, Any]]:
        """
        Resolves a natural language term into its semantic lifecycle concept.
        Returns pure semantic details (concept, target_field, semantic_value, description).
        NO SQL/SOQL/Cypher query syntax is stored or returned.
        """
        lower = text.lower()
        entity_terms = self.data.get("lifecycle_terms", {}).get(entity, {})

        for term_key, term_info in entity_terms.items():
            synonyms = term_info.get("synonyms", [])
            for syn in synonyms:
                if re.search(rf'\b{re.escape(syn)}\b', lower):
                    return {
                        "key": term_key,
                        "concept": term_info.get("concept", term_key),
                        "target_field": term_info.get("target_field"),
                        "semantic_value": term_info.get("semantic_value"),
                        "description": term_info.get("description", term_key),
                        "matched_term": syn
                    }

        # Check learned terms
        learned = self.data.get("learned_terms", {})
        for term, info in learned.items():
            if info.get("target_entity") == entity:
                if re.search(rf'\b{re.escape(term)}\b', lower):
                    return {
                        "key": term,
                        "concept": info.get("concept", "learned_concept"),
                        "target_field": info.get("target_field", "Name"),
                        "semantic_value": info.get("semantic_value", term),
                        "description": info.get("description", f"Learned term: {term}"),
                        "matched_term": term
                    }

        return None

    def is_pure_entity_query(self, entity: str, raw_text: str) -> bool:
        """
        Determines whether the query is purely an inquiry for all records of an entity
        without extra keyword search (e.g. 'company', 'companies', 'pipeline', 'deals', 'leads').
        """
        cleaned = re.sub(r'^(?:get|find|show|search|list|fetch|all|view)\s+', '', raw_text.strip(), flags=re.IGNORECASE).strip().lower()
        synonyms = self.data.get("entities", {}).get(entity, {}).get("synonyms", [])
        return cleaned in synonyms or cleaned in [f"all {s}" for s in synonyms]

    def search_web_for_crm_term(self, term: str) -> Optional[Dict[str, Any]]:
        """
        Queries online knowledge resources (Wikipedia & CRM documentation) to discover
        semantic details for an unknown term (target entity, concept category, description).
        """
        clean_term = term.strip().lower()
        query = f"Salesforce {clean_term} CRM object entity concept"
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&format=json"
        
        headers = {"User-Agent": "SalesforceCRM-LLM-SemanticLearner/2.0"}
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                results = data.get("query", {}).get("search", [])
                combined_text = " ".join([r.get("title", "") + " " + r.get("snippet", "") for r in results]).lower()

                entity_scores = {"Account": 0, "Opportunity": 0, "Contact": 0, "Lead": 0}
                if any(w in combined_text for w in ["deal", "revenue", "pipeline", "stage", "closed won", "opportunity", "bid"]):
                    entity_scores["Opportunity"] += 2
                if any(w in combined_text for w in ["company", "organization", "account", "client", "firm", "customer", "vendor"]):
                    entity_scores["Account"] += 2
                if any(w in combined_text for w in ["person", "people", "contact", "individual", "employee", "title"]):
                    entity_scores["Contact"] += 2
                if any(w in combined_text for w in ["prospect", "inquiry", "unqualified", "qualification", "lead"]):
                    entity_scores["Lead"] += 2

                best_entity = max(entity_scores, key=entity_scores.get)
                if entity_scores[best_entity] > 0:
                    return {
                        "term": clean_term,
                        "target_entity": best_entity,
                        "concept": f"learned_{best_entity.lower()}_concept",
                        "description": f"Discovered CRM concept associated with {best_entity}",
                        "source": "Wikipedia / Online CRM Index"
                    }
        except Exception as e:
            print(f"[CRMDictionary] Web search error for '{term}': {e}")

        # Fallback heuristic
        lower = clean_term
        if any(w in lower for w in ["deal", "bid", "opp", "pipeline", "sale"]):
            return {"term": clean_term, "target_entity": "Opportunity", "concept": "pipeline_deal", "description": "Opportunity deal concept", "source": "Internal Heuristic"}
        if any(w in lower for w in ["firm", "corp", "agency", "business", "company", "vendor"]):
            return {"term": clean_term, "target_entity": "Account", "concept": "organization", "description": "Account organization concept", "source": "Internal Heuristic"}
        if any(w in lower for w in ["staff", "worker", "rep", "stakeholder", "exec", "person"]):
            return {"term": clean_term, "target_entity": "Contact", "concept": "individual_person", "description": "Contact person concept", "source": "Internal Heuristic"}
        if any(w in lower for w in ["suspect", "inbound", "subscriber", "lead"]):
            return {"term": clean_term, "target_entity": "Lead", "concept": "inbound_lead", "description": "Inbound lead concept", "source": "Internal Heuristic"}

        return None

    def learn_and_persist_term(self, term: str, context_sobject: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Discovers an unknown term via web search, extracts pure semantic details,
        and saves it into crm_dictionary.json under learned_terms with NO query syntax.
        """
        clean_term = term.strip().lower()
        if not clean_term:
            return None

        # Check existing entity synonyms
        for ent, info in self.data.get("entities", {}).items():
            if clean_term in info.get("synonyms", []):
                return {"target_entity": ent, "cached": True}

        core_keyword = re.sub(r'^(?:get|find|show|search|list|fetch|all|view)\s+', '', clean_term).strip()
        core_keyword = re.sub(r'\b(?:all|the|my|our)\b', '', core_keyword).strip()
        search_target = core_keyword if core_keyword else clean_term

        if search_target in self.data.get("learned_terms", {}):
            return self.data["learned_terms"][search_target]

        discovered = self.search_web_for_crm_term(search_target)
        if discovered:
            target_entity = discovered["target_entity"]
            
            entry = {
                "term": search_target,
                "target_entity": target_entity,
                "target_field": "Name",
                "concept": discovered.get("concept", "entity_attribute_search"),
                "description": discovered.get("description", f"Learned CRM concept for {target_entity}"),
                "source": discovered.get("source", "Web Search"),
                "learned_at": datetime.utcnow().isoformat() + "Z"
            }
            
            if "learned_terms" not in self.data:
                self.data["learned_terms"] = {}
            self.data["learned_terms"][search_target] = entry

            # Add to entity synonyms if it is a single word or 2-word concept
            if len(search_target.split()) <= 2:
                syns = self.data.setdefault("entities", {}).setdefault(target_entity, {}).setdefault("synonyms", [])
                if search_target not in syns:
                    syns.append(search_target)

            self.save()
            print(f"[CRMDictionary] Learned & saved semantic details for: '{search_target}' ➔ {target_entity}")
            return entry

        return None

# Singleton instance
crm_dictionary = CRMDictionary()
