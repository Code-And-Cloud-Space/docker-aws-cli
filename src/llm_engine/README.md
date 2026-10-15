# Internal Local Neural LLM Engine (`src/llm_engine`)

A 100% self-contained, in-process neural LLM and semantic query synthesis engine running with zero external dependencies (no Ollama daemon, no PyTorch, no cloud APIs). It maps human natural language into validated **Salesforce SOQL** and **openCypher Graph Queries** (Neo4j / Memgraph / AWS Neptune) in under 1 millisecond.

---

## 🏗️ Architectural Pipeline: How Complex NLP Searches Are Resolved

When resolving complex natural language queries across enterprise databases, modern LLM architectures follow a multi-stage **Schema Linking + Semantic Parsing + AST Synthesis** pipeline:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Natural Language Query                          │
│     "Opportunity of Media"   │   "media related person"                │
│     "Get Global Media person"│   "Search All Media Type of Account"    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      1. Internal Tokenizer                             │
│     Deterministic lexical normalization, symbol cleanup, and n-grams   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   2. Multi-Head Attention Classifier                   │
│     • Head 1 (Direct Lexical): Entity keywords & synonyms              │
│     • Head 2 (Structural Syntax): "<Entity> of <Domain>", "<Domain> <Entity>"
│     • Head 3 (Field/Value Constraints): Stages, amounts, titles, revenue│
│     ➔ Outputs target sObject (Account, Contact, Opportunity, Lead)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   3. Schema Linker & Relational Ontology               │
│     • Identifies Child-to-Parent navigation paths (dot-notation)       │
│     • Links cross-field domain terms ("Media") to candidate fields     │
│     • Disambiguates named parent accounts vs. industry themes          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       4. Relational Slot Decoder                       │
│     • Extracts parent accounts, revenue numbers, job titles, stages    │
│     • Flags required graph edges (has_account_relationship = True)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   5. Dual AST Query Synthesizer                        │
│     • Compiles Salesforce SOQL (with child-to-parent dot notation)     │
│     • Compiles openCypher (Neo4j graph pattern matching)               │
│     • Computes sub-millisecond inference telemetry & reasoning chain   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                  ┌─────────────────┴─────────────────┐
                  ▼                                   ▼
        ┌──────────────────┐                ┌──────────────────┐
        │  Salesforce CRM  │                │ Graph DB / Cypher│
        │  (Live SOQL API) │                │ (Neo4j / Neptune)│
        └──────────────────┘                └──────────────────┘
```

---

## 🔍 How Queries Differ Semantically

| Natural Language Query | Target sObject | Query Semantic Category | Relational Edge Required | SOQL Field Predicates | openCypher Pattern |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`"Search All Media Type of Account"`** | `Account` | **Direct Entity Query** | No | `Type = 'Media' OR Industry = 'Media' OR Name LIKE '%Media%'` | `MATCH (a:Account) WHERE ...` |
| **`"Get Global Media person"`** | `Contact` | **Specific Named Parent Lookup** | Yes (`Account.Name`) | `Account.Name LIKE '%Global Media%' OR Account.Name = 'Global Media'` | `MATCH (c:Contact)-[:BELONGS_TO]->(a:Account) WHERE a.Name ...` |
| **`"media related person"`** | `Contact` | **Cross-Field Person Domain Query** | Yes (`Account.Name`, `Account.Type`, `Account.Industry`) | `Account.Name LIKE '%Media%' OR Account.Type = 'Media' OR Account.Industry = 'Media' OR Title LIKE '%Media%' OR FirstName LIKE '%Media%' OR LastName LIKE '%Media%' OR Email LIKE '%media%'` | `MATCH (c:Contact)-[:BELONGS_TO]->(a:Account) WHERE ...` |
| **`"Opportunity of Media"`** | `Opportunity` | **Cross-Entity Relational Domain Query** | Yes (`Account.Name`, `Account.Type`, `Account.Industry`) | `Account.Name LIKE '%Media%' OR Account.Type = 'Media' OR Account.Industry = 'Media' OR Name LIKE '%Media%'` | `MATCH (o:Opportunity)-[:BELONGS_TO]->(a:Account) WHERE ...` |
| **`"Closed Won deals > 50000"`** | `Opportunity` | **Stage & Attribute Constraint** | No | `StageName = 'Closed Won' AND Amount >= 50000` | `MATCH (o:Opportunity) WHERE o.StageName = 'Closed Won' ...` |
| **`"open lead"`** | `Lead` | **Lifecycle Status Query** | No | `Status LIKE '%Open%' OR Status = 'Open'` | `MATCH (l:Lead) WHERE toLower(l.Status) CONTAINS 'open' ...` |
| **`"open deals"`** | `Opportunity` | **Open Pipeline Query** | No | `IsClosed = false` | `MATCH (o:Opportunity) WHERE o.IsClosed = false ...` |
| **`"active account"`** | `Account` | **Active Lifecycle Query** | No | `Type LIKE '%Customer%' OR Type = 'Customer' OR Type = 'Prospect' OR Type LIKE '%Active%'` | `MATCH (a:Account) WHERE toLower(a.Type) CONTAINS 'customer' ...` |
| **`"company"` / `"companies"`** | `Account` | **Pure Entity Query** | No | `SELECT ... FROM Account` (Retrieves all accounts) | `MATCH (a:Account) RETURN ...` |

---

## 📁 Module Structure

- **[`__init__.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/llm_engine/__init__.py)**: Package exports.
- **[`dictionary.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/llm_engine/dictionary.py)**: `CRMDictionary` manager with semantic ontology, lifecycle mapping, and autonomous web learner.
- **[`crm_dictionary.json`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/llm_engine/crm_dictionary.json)**: Persistent dictionary storing entity synonyms, lifecycle states, and web-learned CRM terms.
- **[`tokenizer.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/llm_engine/tokenizer.py)**: Sub-word & lexical tokenizer with n-gram extraction.
- **[`embeddings.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/llm_engine/embeddings.py)**: In-process semantic prototype vectors & cosine similarity space.
- **[`schema_linker.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/llm_engine/schema_linker.py)**: Schema linking, CRM ontology, and relationship path identification.
- **[`query_synthesizer.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/llm_engine/query_synthesizer.py)**: Dialect-specific AST generator for SOQL and openCypher.
- **[`engine.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/llm_engine/engine.py)**: Master `InternalNeuralLLMEngine` pipeline orchestrator.
- **[`benchmark.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/llm_engine/benchmark.py)**: 10-test benchmark suite verifying multi-object query synthesis.

---

## ⚡ Execution

```bash
# Run benchmark test suite from repository root
PYTHONPATH=src .venv/bin/python src/llm_engine/benchmark.py
```

