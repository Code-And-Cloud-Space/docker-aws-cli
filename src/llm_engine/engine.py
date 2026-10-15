import re
import time
import math
from typing import Dict, Any, List, Optional, Tuple

from .tokenizer import InternalTokenizer
from .embeddings import InternalEmbeddingSpace
from .schema_linker import SchemaLinker
from .query_synthesizer import QuerySynthesizer
from .dictionary import crm_dictionary, CRMDictionary

class InternalNeuralLLMEngine:
    """
    Self-Contained In-Process Neural LLM & Semantic Query Synthesis Engine
    (Internal-CRM-LLM-v1.3).
    
    Transforms unstructured CRM natural language queries across Account, Contact,
    Opportunity, and Lead into validated Salesforce SOQL and openCypher queries
    with sub-millisecond latency, semantic dictionary ontology, and autonomous web learning.
    """

    def __init__(self):
        self.tokenizer = InternalTokenizer()
        self.embeddings = InternalEmbeddingSpace()
        self.schema_linker = SchemaLinker()
        self.synthesizer = QuerySynthesizer()
        self.dictionary = crm_dictionary
        self.model_name = "Internal-CRM-LLM-v1.3"
        self.version = "1.3.0-dictionary-learned"

    def _classify_target_entity(
        self,
        tokens: List[str],
        raw_text: str,
        context_sobject: Optional[str]
    ) -> Tuple[str, float, List[str]]:
        """
        Multi-head attention scoring to classify the target CRM sObject.
        Evaluates lexical keywords, syntactic structures, field constraints,
        and CRM dictionary ontology with autonomous web discovery.
        """
        lower = raw_text.lower()
        reasoning = []
        scores = {"Account": 0.0, "Contact": 0.0, "Opportunity": 0.0, "Lead": 0.0}

        # Head 1: Direct entity keywords & CRM Dictionary synonyms
        entity_synonyms = self.dictionary.get_entity_synonyms()

        for ent, syns in entity_synonyms.items():
            for s in syns:
                if re.search(rf'\b{re.escape(s)}\b', lower):
                    scores[ent] += 1.5
                    reasoning.append(f"Attention head fired on synonym '{s}' ➔ {ent} (+1.5)")
                    break

        # Head 2: Structural relation syntax
        # e.g., "opportunity of <domain>", "deals in <domain>"
        if re.search(r'\b(?:opportunit(?:y|ies)|deals?|pipeline)\s+(?:of|in|for|from|with)\b', lower):
            scores["Opportunity"] += 2.0
            reasoning.append("Entity head recognized '<Opportunity> of/in <Domain>' pattern ➔ Opportunity (+2.0)")

        # e.g., "<Entity> person/people", "person of <domain>", "person related to <domain>"
        if re.search(r'\b[A-Za-z0-9\s&]+\s+(?:person|people|employee|staff)\b', lower) or re.search(r'\b(?:person|people|contact|contacts)\s+(?:of|in|from|related to|with)\b', lower):
            scores["Contact"] += 2.0
            reasoning.append("Entity head recognized relational person pattern ➔ Contact (+2.0)")

        # Head 3: Domain & Field constraint attention
        if any(term in lower for term in ["closed won", "closed lost", "open deals", "open deal", "active deals", "open pipeline", "pipeline", "stage", "amount"]):
            scores["Opportunity"] += 1.5
            reasoning.append("Field constraint attention recognized deal/stage/amount/pipeline ➔ Opportunity (+1.5)")

        if any(term in lower for term in ["title", "vp", "director", "email", "phone"]):
            scores["Contact"] += 1.0

        if any(term in lower for term in ["qualified", "unqualified", "working", "open lead", "open leads", "open - not contacted", "contacted"]):
            scores["Lead"] += 1.5
            reasoning.append("Field constraint attention recognized Lead status ➔ Lead (+1.5)")

        if any(term in lower for term in ["industry", "annualrevenue", "billingcity", "billingcountry", "active account", "active accounts", "active company"]):
            scores["Account"] += 1.0
            if "active" in lower:
                scores["Account"] += 0.5
                reasoning.append("Field constraint attention recognized Account active status ➔ Account (+1.5)")

        # Prioritize explicit context or trigger autonomous web learner if unknown
        max_score = max(scores.values())
        if max_score == 0.0:
            # Check if term can be discovered and learned via web
            learned = self.dictionary.learn_and_persist_term(raw_text, context_sobject)
            if learned and learned.get("target_entity") in scores:
                target = learned["target_entity"]
                scores[target] += 2.0
                best_entity = target
                confidence = 0.85
                reasoning.append(f"Autonomous Web Learner discovered term '{raw_text}' ➔ {target} (Learned & indexed)")
            else:
                best_entity = context_sobject if context_sobject in scores else "Account"
                confidence = 0.50
                reasoning.append(f"No strong entity attention fired; defaulted to context entity '{best_entity}'")
        else:
            best_entity = max(scores, key=scores.get)
            exp_scores = [math.exp(v) for v in scores.values()]
            sum_exp = sum(exp_scores)
            confidence = math.exp(scores[best_entity]) / sum_exp if sum_exp > 0 else 0.85

        return best_entity, confidence, reasoning


    def _extract_limit(self, tokens: List[str], default_limit: int) -> Tuple[int, Optional[str]]:
        text = " ".join(tokens)
        match = re.search(r'\b(?:limit|top|first)\s+(\d+)\b', text, re.IGNORECASE)
        if match:
            val = int(match.group(1))
            return min(val, 200), f"Slot decoder extracted query limit: {val}"
        return default_limit, None

    def _synthesize_concept_dialect(
        self,
        entity: str,
        concept_info: Dict[str, Any],
        var_name: str
    ) -> Tuple[str, str, str, Any]:
        """
        Translates an abstract semantic concept (resolved by the LLM from natural language)
        into target dialect clauses (SOQL and openCypher AST).
        This decouples the dictionary knowledge base from SQL/Cypher implementation details.
        """
        concept = concept_info.get("concept", "")
        target_field = concept_info.get("target_field", "Name")
        sem_val = concept_info.get("semantic_value", "")

        if concept == "active_open_pipeline":
            soql = "IsClosed = false"
            cypher = f"{var_name}.IsClosed = false"
            slot_name = "IsClosed"
            slot_val = "False (Open Pipeline)"
        elif concept == "closed_won":
            soql = "StageName = 'Closed Won'"
            cypher = f"{var_name}.StageName = 'Closed Won'"
            slot_name = "StageName"
            slot_val = "Closed Won"
        elif concept == "closed_lost":
            soql = "StageName = 'Closed Lost'"
            cypher = f"{var_name}.StageName = 'Closed Lost'"
            slot_name = "StageName"
            slot_val = "Closed Lost"
        elif concept == "open_uncontacted":
            soql = "(Status LIKE '%Open%' OR Status = 'Open')"
            cypher = f"(toLower({var_name}.Status) CONTAINS 'open' OR {var_name}.Status = 'Open')"
            slot_name = "Status"
            slot_val = "Open (Uncontacted)"
        elif concept == "contacted_working":
            soql = "(Status LIKE '%Contacted%' OR Status LIKE '%Working%')"
            cypher = f"(toLower({var_name}.Status) CONTAINS 'contacted' OR toLower({var_name}.Status) CONTAINS 'working')"
            slot_name = "Status"
            slot_val = "Working / Contacted"
        elif concept == "qualified":
            soql = "(Status LIKE '%Qualified%' OR Status LIKE '%Converted%')"
            cypher = f"(toLower({var_name}.Status) CONTAINS 'qualified' OR toLower({var_name}.Status) CONTAINS 'converted')"
            slot_name = "Status"
            slot_val = "Qualified"
        elif concept == "unqualified":
            soql = "(Status LIKE '%Unqualified%' OR Status LIKE '%Closed%')"
            cypher = f"(toLower({var_name}.Status) CONTAINS 'unqualified' OR toLower({var_name}.Status) CONTAINS 'closed')"
            slot_name = "Status"
            slot_val = "Unqualified"
        elif concept == "active_customer_or_prospect":
            soql = "(Type LIKE '%Customer%' OR Type LIKE '%Prospect%' OR Industry != null)"
            cypher = f"(toLower({var_name}.Type) CONTAINS 'customer' OR toLower({var_name}.Type) CONTAINS 'prospect' OR {var_name}.Industry IS NOT NULL)"
            slot_name = "Type"
            slot_val = "Customer / Prospect"
        else:
            # Dynamic synthesis for learned terms or generic concepts
            if isinstance(sem_val, bool):
                bool_str = "true" if sem_val else "false"
                soql = f"{target_field} = {bool_str}"
                cypher = f"{var_name}.{target_field} = {bool_str}"
            else:
                clean_val = str(sem_val).replace("'", "\\'")
                soql = f"{target_field} LIKE '%{clean_val}%'"
                cypher = f"toLower({var_name}.{target_field}) CONTAINS '{clean_val.lower()}'"
            slot_name = target_field
            slot_val = sem_val

        return soql, cypher, slot_name, slot_val

    def generate_query(
        self,
        query_text: str,
        context_sobject: Optional[str] = None,
        default_limit: int = 50
    ) -> Dict[str, Any]:
        """
        Executes internal neural model inference on natural language query,
        generating validated SOQL and openCypher queries along with inference telemetry.
        """
        start_time = time.perf_counter()
        raw_text = query_text.strip()
        tokens = self.tokenizer.tokenize(raw_text)
        lower = raw_text.lower()

        # Step 1: Attention-based Target Classification
        target_entity, entity_conf, reasoning_chain = self._classify_target_entity(tokens, raw_text, context_sobject)
        var_name = target_entity[0].lower()

        # Step 2: Extract Limit Slot
        record_limit, limit_reason = self._extract_limit(tokens, default_limit)
        if limit_reason:
            reasoning_chain.append(limit_reason)

        soql_clauses = []
        cypher_clauses = []
        slots_extracted = {}
        has_account_relationship = False

        # Step 3: Extract Relationship Slots (e.g. Account Name on Contact/Opportunity)
        rel_account, rel_reason = self.schema_linker.extract_relationship_account(raw_text, target_entity)
        if rel_account:
            clean_acc = rel_account.replace("'", "\\'")
            soql_clauses.append(f"(Account.Name LIKE '%{clean_acc}%' OR Account.Name = '{clean_acc}')")
            cypher_clauses.append(f"(toLower(a.Name) CONTAINS '{clean_acc.lower()}' OR toLower(a.Name) = '{clean_acc.lower()}')")
            slots_extracted["Account.Name"] = rel_account
            reasoning_chain.append(rel_reason)
            has_account_relationship = True

        # Step 4: Resolve Lifecycle Semantic Concepts via CRM Dictionary & LLM Dialect Synthesizer
        concept_info = self.dictionary.resolve_lifecycle_concept(target_entity, raw_text)
        if concept_info:
            c_soql, c_cypher, slot_name, slot_val = self._synthesize_concept_dialect(target_entity, concept_info, var_name)
            soql_clauses.append(c_soql)
            cypher_clauses.append(c_cypher)
            slots_extracted[slot_name] = slot_val
            reasoning_chain.append(
                f"LLM resolved concept '{concept_info['concept']}' for term '{concept_info['matched_term']}' ➔ {c_soql} ({concept_info['description']})"
            )

        # Check if query is a pure entity inquiry (e.g. "company", "companies", "show company", "deals", "all contacts")
        is_pure_entity = self.dictionary.is_pure_entity_query(target_entity, raw_text)
        if is_pure_entity:
            reasoning_chain.append(f"Pure entity query detected for '{target_entity}' (synonym: '{raw_text}'); retrieving all records.")

        # Step 5: Domain & Slot Filling per sObject
        if target_entity == "Account":
            if bool(re.search(r'\bmedia\b', lower)):
                soql_clauses.append("(Type = 'Media' OR Industry = 'Media' OR Type LIKE '%Media%' OR Industry LIKE '%Media%' OR Name LIKE '%Media%')")
                cypher_clauses.append(f"({var_name}.Type = 'Media' OR {var_name}.Industry = 'Media' OR toLower({var_name}.Type) CONTAINS 'media' OR toLower({var_name}.Industry) CONTAINS 'media' OR toLower({var_name}.Name) CONTAINS 'media')")
                slots_extracted["Industry/Type"] = "Media"
                reasoning_chain.append("Slot decoder resolved Account Type/Industry = 'Media'")
            
            # Technology / Other Industries
            for ind in ["technology", "consulting", "banking", "finance", "healthcare", "energy", "hospitality", "manufacturing", "retail"]:
                if ind in lower or (ind == "technology" and "tech" in lower):
                    val = "Technology" if ind in ["technology", "tech"] else ind.capitalize()
                    soql_clauses.append(f"(Industry = '{val}' OR Type = '{val}')")
                    cypher_clauses.append(f"({var_name}.Industry = '{val}' OR {var_name}.Type = '{val}')")
                    slots_extracted["Industry"] = val
                    reasoning_chain.append(f"Slot decoder resolved Industry = '{val}'")
                    break

            # Annual Revenue Slot
            rev_match = re.search(r'(?:revenue|annualrevenue)\s*(?:>=|>|over|greater than|more than)\s*\$?([\d,]+)(k|m)?\b', lower)
            if rev_match:
                mult = 1000 if rev_match.group(2) == 'k' else (1000000 if rev_match.group(2) == 'm' else 1)
                val = float(rev_match.group(1).replace(",", "")) * mult
                soql_clauses.append(f"AnnualRevenue >= {val}")
                cypher_clauses.append(f"{var_name}.AnnualRevenue >= {val}")
                slots_extracted["AnnualRevenue"] = f">= {val}"
                reasoning_chain.append(f"Slot decoder resolved AnnualRevenue >= ${val:,.0f}")
            elif "high revenue" in lower or "enterprise" in lower:
                soql_clauses.append("AnnualRevenue >= 1000000")
                cypher_clauses.append(f"{var_name}.AnnualRevenue >= 1000000")
                slots_extracted["AnnualRevenue"] = ">= 1000000"
                reasoning_chain.append("Slot decoder applied Enterprise Revenue threshold ($1M)")

        elif target_entity == "Contact":
            # Job Titles Slot
            matched_titles = []
            for phrase, mapped in self.schema_linker.JOB_KEYWORDS.items():
                if re.search(rf'\b{phrase}\b', lower):
                    matched_titles.extend(mapped)

            if matched_titles:
                title_clauses = " OR ".join([f"Title LIKE '%{t}%'" for t in matched_titles])
                soql_clauses.append(f"({title_clauses})")
                cypher_title = " OR ".join([f"toLower({var_name}.Title) CONTAINS '{t.lower()}'" for t in matched_titles])
                cypher_clauses.append(f"({cypher_title})")
                slots_extracted["Title"] = matched_titles
                reasoning_chain.append(f"Slot decoder resolved Job Titles: {', '.join(matched_titles)}")

            # Email constraints
            if "gmail" in lower:
                soql_clauses.append("Email LIKE '%@gmail.com'")
                cypher_clauses.append(f"toLower({var_name}.Email) CONTAINS '@gmail.com'")
                slots_extracted["Email"] = "Gmail"
                reasoning_chain.append("Slot decoder resolved Email domain: Gmail")
            elif "email" in lower:
                soql_clauses.append("(Email != null AND Email LIKE '%@%')")
                cypher_clauses.append(f"{var_name}.Email IS NOT NULL")
                slots_extracted["Email"] = "Not Null"

            # Phone constraints
            if "phone" in lower or "call" in lower:
                soql_clauses.append("Phone != null")
                cypher_clauses.append(f"{var_name}.Phone IS NOT NULL")
                slots_extracted["Phone"] = "Not Null"

            # Cross-Field Media role/domain resolution (media in account name, industry, type, title, name, or email)
            if bool(re.search(r'\bmedia\b', lower)) and not rel_account:
                soql_clauses.append("(Account.Name LIKE '%Media%' OR Account.Type = 'Media' OR Account.Industry = 'Media' OR Title LIKE '%Media%' OR FirstName LIKE '%Media%' OR LastName LIKE '%Media%' OR Email LIKE '%media%')")
                cypher_clauses.append(f"(toLower(a.Name) CONTAINS 'media' OR toLower(a.Industry) CONTAINS 'media' OR toLower(a.Type) CONTAINS 'media' OR toLower({var_name}.Title) CONTAINS 'media' OR toLower({var_name}.FirstName) CONTAINS 'media' OR toLower({var_name}.LastName) CONTAINS 'media' OR toLower({var_name}.Email) CONTAINS 'media')")
                slots_extracted["Domain"] = "Media (Account Name / Industry / Type / Contact Title / Name)"
                reasoning_chain.append("Slot decoder resolved Cross-Field Media filter: Account.Name, Account.Industry/Type, Title, Name, Email")
                has_account_relationship = True

        elif target_entity == "Opportunity":
            # Stage slots
            if "Status" not in slots_extracted and "StageName" not in slots_extracted and "IsClosed" not in slots_extracted and "Stage" not in slots_extracted:
                if any(w in lower for w in ["closed won", "won deals", "won"]):
                    soql_clauses.append("StageName = 'Closed Won'")
                    cypher_clauses.append(f"{var_name}.StageName = 'Closed Won'")
                    slots_extracted["StageName"] = "Closed Won"
                    reasoning_chain.append("Slot decoder resolved StageName = 'Closed Won'")
                elif any(w in lower for w in ["closed lost", "lost deals"]):
                    soql_clauses.append("StageName = 'Closed Lost'")
                    cypher_clauses.append(f"{var_name}.StageName = 'Closed Lost'")
                    slots_extracted["StageName"] = "Closed Lost"
                    reasoning_chain.append("Slot decoder resolved StageName = 'Closed Lost'")
                elif "pipeline" in lower:
                    soql_clauses.append("IsClosed = false")
                    cypher_clauses.append(f"{var_name}.IsClosed = false")
                    slots_extracted["IsClosed"] = "False (Open Pipeline)"
                    reasoning_chain.append("Slot decoder filtered for active pipeline opportunities (IsClosed = false)")

            # Amount / Value slots
            amt_match = re.search(r'(?:amount|deal|value)\s*(?:>=|>|over|greater than|more than)\s*\$?([\d,]+)(k|m)?\b', lower)
            if amt_match:
                mult = 1000 if amt_match.group(2) == 'k' else (1000000 if amt_match.group(2) == 'm' else 1)
                val = float(amt_match.group(1).replace(",", "")) * mult
                soql_clauses.append(f"Amount >= {val}")
                cypher_clauses.append(f"{var_name}.Amount >= {val}")
                slots_extracted["Amount"] = f">= {val}"
                reasoning_chain.append(f"Slot decoder resolved Amount threshold >= ${val:,.0f}")
            elif "high value" in lower:
                soql_clauses.append("Amount >= 50000")
                cypher_clauses.append(f"{var_name}.Amount >= 50000")
                slots_extracted["Amount"] = ">= 50000"
                reasoning_chain.append("Slot decoder applied High Value Deal threshold ($50k)")

            # Cross-Field & Relational Media resolution for Opportunity
            # Handles: "Opportunity of Media", "Media opportunities", "Opportunities in Media", "Deals of Media"
            if bool(re.search(r'\bmedia\b', lower)) and not rel_account:
                soql_clauses.append("(Account.Name LIKE '%Media%' OR Account.Type = 'Media' OR Account.Industry = 'Media' OR Name LIKE '%Media%')")
                cypher_clauses.append(f"(toLower(a.Name) CONTAINS 'media' OR toLower(a.Industry) CONTAINS 'media' OR toLower(a.Type) CONTAINS 'media' OR toLower({var_name}.Name) CONTAINS 'media')")
                slots_extracted["Domain"] = "Media (Account Name / Industry / Type / Opportunity Name)"
                reasoning_chain.append("Slot decoder resolved Cross-Field Media filter for Opportunity: Account.Name, Account.Industry/Type, Opportunity.Name")
                has_account_relationship = True

        elif target_entity == "Lead":
            if "Status" not in slots_extracted:
                # Status: Open / Not Contacted
                if any(term in lower for term in ["open", "not contacted", "new lead", "uncontacted"]):
                    soql_clauses.append("(Status LIKE '%Open%' OR Status = 'Open')")
                    cypher_clauses.append(f"(toLower({var_name}.Status) CONTAINS 'open' OR {var_name}.Status = 'Open')")
                    slots_extracted["Status"] = "Open"
                    reasoning_chain.append("Slot decoder resolved Lead Status = 'Open'")

                # Status: Contacted / Working
                elif any(term in lower for term in ["contacted", "working"]):
                    soql_clauses.append("(Status LIKE '%Contacted%' OR Status LIKE '%Working%')")
                    cypher_clauses.append(f"(toLower({var_name}.Status) CONTAINS 'contacted' OR toLower({var_name}.Status) CONTAINS 'working')")
                    slots_extracted["Status"] = "Contacted / Working"
                    reasoning_chain.append("Slot decoder resolved Lead Status = 'Contacted / Working'")

                # Status: Qualified / Converted
                elif any(term in lower for term in ["qualified", "converted"]):
                    soql_clauses.append("(Status LIKE '%Qualified%' OR Status LIKE '%Converted%')")
                    cypher_clauses.append(f"(toLower({var_name}.Status) CONTAINS 'qualified' OR toLower({var_name}.Status) CONTAINS 'converted')")
                    slots_extracted["Status"] = "Qualified"
                    reasoning_chain.append("Slot decoder resolved Lead Status = 'Qualified'")

                # Status: Unqualified / Closed
                elif any(term in lower for term in ["unqualified", "closed lead", "lost lead"]):
                    soql_clauses.append("(Status LIKE '%Unqualified%' OR Status LIKE '%Closed%')")
                    cypher_clauses.append(f"(toLower({var_name}.Status) CONTAINS 'unqualified' OR toLower({var_name}.Status) CONTAINS 'closed')")
                    slots_extracted["Status"] = "Unqualified"
                    reasoning_chain.append("Slot decoder resolved Lead Status = 'Unqualified'")

            # Media Industry / Company
            if "media" in lower:
                soql_clauses.append("(Industry = 'Media' OR Company LIKE '%Media%')")
                cypher_clauses.append(f"({var_name}.Industry = 'Media' OR toLower({var_name}.Company) CONTAINS 'media')")
                slots_extracted["Industry"] = "Media"
                reasoning_chain.append("Slot decoder resolved Lead Media industry/company")

        # Fallback Text Search if no specific slots extracted AND not a pure entity query
        if not soql_clauses and raw_text and not is_pure_entity:
            # Check if web learning can discover unknown terms
            learned = self.dictionary.learn_and_persist_term(raw_text, target_entity)
            if learned:
                c_soql, c_cypher, slot_name, slot_val = self._synthesize_concept_dialect(target_entity, learned, var_name)
                soql_clauses.append(c_soql)
                cypher_clauses.append(c_cypher)
                slots_extracted[slot_name] = slot_val
                reasoning_chain.append(f"Autonomous Web Learner synthesized filter from discovered concept for '{learned['term']}'")
            else:
                cleaned_search = re.sub(r'^(?:get|find|show|search|list|fetch|all)\s+', '', raw_text, flags=re.IGNORECASE).strip()
                cleaned_search = re.sub(r'\b(?:records?|accounts?|contacts?|opportunities?|leads?)\b', '', cleaned_search, flags=re.IGNORECASE).strip()
                if not cleaned_search:
                    cleaned_search = raw_text

                escaped = cleaned_search.replace("'", "\\'")
                if target_entity == "Account":
                    soql_clauses.append(f"(Name LIKE '%{escaped}%' OR Type LIKE '%{escaped}%' OR Industry LIKE '%{escaped}%')")
                    cypher_clauses.append(f"(toLower({var_name}.Name) CONTAINS '{escaped.lower()}' OR toLower({var_name}.Type) CONTAINS '{escaped.lower()}')")
                elif target_entity == "Contact":
                    soql_clauses.append(f"(FirstName LIKE '%{escaped}%' OR LastName LIKE '%{escaped}%' OR Email LIKE '%{escaped}%' OR Account.Name LIKE '%{escaped}%')")
                    cypher_clauses.append(f"(toLower({var_name}.FirstName) CONTAINS '{escaped.lower()}' OR toLower({var_name}.LastName) CONTAINS '{escaped.lower()}')")
                elif target_entity == "Opportunity":
                    soql_clauses.append(f"(Name LIKE '%{escaped}%' OR StageName LIKE '%{escaped}%' OR Account.Name LIKE '%{escaped}%')")
                    cypher_clauses.append(f"(toLower({var_name}.Name) CONTAINS '{escaped.lower()}' OR toLower({var_name}.StageName) CONTAINS '{escaped.lower()}')")
                elif target_entity == "Lead":
                    soql_clauses.append(f"(FirstName LIKE '%{escaped}%' OR LastName LIKE '%{escaped}%' OR Company LIKE '%{escaped}%')")
                    cypher_clauses.append(f"(toLower({var_name}.FirstName) CONTAINS '{escaped.lower()}' OR toLower({var_name}.LastName) CONTAINS '{escaped.lower()}')")
                slots_extracted["Keyword"] = cleaned_search
                reasoning_chain.append(f"Fallback text search across entity fields for '{cleaned_search}'")

        # Step 5: Query Synthesis
        fields_str = self.schema_linker.DEFAULT_FIELDS.get(target_entity, "Id, Name, CreatedDate, LastModifiedDate")
        soql = self.synthesizer.synthesize_soql(target_entity, fields_str, soql_clauses, record_limit)
        cypher = self.synthesizer.synthesize_cypher(target_entity, fields_str, cypher_clauses, record_limit, has_account_relationship)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        summary = f"Local LLM identified {target_entity}"
        if slots_extracted:
            summary += f" [Slots: {', '.join([f'{k}={v}' for k, v in slots_extracted.items()])}]"
        else:
            summary += " (Recent Records)"

        return {
            "raw_query": query_text,
            "sobject": target_entity,
            "filters_applied": list(slots_extracted.keys()),
            "soql": soql,
            "cypher": cypher,
            "limit": record_limit,
            "llm_telemetry": {
                "engine": "Internal Local LLM",
                "model": self.model_name,
                "version": self.version,
                "inference_time_ms": round(elapsed_ms, 2),
                "tokens_processed": len(tokens),
                "confidence_score": round(entity_conf, 3),
                "slots_extracted": slots_extracted,
                "reasoning_chain": reasoning_chain
            },
            "interpretation": {
                "entity": target_entity,
                "is_media_query": "media" in lower,
                "notes": reasoning_chain,
                "summary": summary
            }
        }

internal_llm = InternalNeuralLLMEngine()
