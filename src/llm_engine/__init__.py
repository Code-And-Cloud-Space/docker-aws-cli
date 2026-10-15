"""
Internal Neural LLM Engine - Core Package
100% In-Process, Zero-External-Dependency Local CRM Query Synthesizer
Translates natural language to Salesforce SOQL and openCypher Graph queries.
"""

from .engine import InternalNeuralLLMEngine, internal_llm
from .tokenizer import InternalTokenizer
from .embeddings import InternalEmbeddingSpace
from .schema_linker import SchemaLinker
from .query_synthesizer import QuerySynthesizer
from .dictionary import CRMDictionary, crm_dictionary

__all__ = [
    "InternalNeuralLLMEngine",
    "internal_llm",
    "InternalTokenizer",
    "InternalEmbeddingSpace",
    "SchemaLinker",
    "QuerySynthesizer",
    "CRMDictionary",
    "crm_dictionary",
]

