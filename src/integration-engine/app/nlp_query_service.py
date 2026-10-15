from typing import Dict, Any, Optional
from .internal_llm import internal_llm

class NLPQueryService:
    """
    Multi-Object Natural Language Processing (NLP) Query Engine powered by
    Self-Contained Internal Local Neural LLM (Internal-CRM-LLM-v1.0).
    Translates natural language requests across Account, Contact, Opportunity, Lead, etc.
    into optimized Salesforce SOQL and openCypher/Neo4j graph queries completely in-process
    with zero external dependencies or external servers.
    """

    def parse_nlp_query(self, query_text: str, context_sobject: Optional[str] = None, default_limit: int = 50) -> Dict[str, Any]:
        """
        Parses an NLP query using the internal local neural LLM engine.
        """
        return internal_llm.generate_query(
            query_text=query_text, 
            context_sobject=context_sobject, 
            default_limit=default_limit
        )

nlp_service = NLPQueryService()
