"""
Compatibility Adapter for Internal Neural LLM Engine.
Imports directly from the standalone module: src/llm_engine
"""

import sys
from pathlib import Path

# Ensure root src is in sys.path
root_src = str(Path(__file__).resolve().parent.parent.parent)
app_dir = str(Path(__file__).resolve().parent.parent)
for p in ["/app", root_src, app_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from llm_engine import internal_llm, InternalNeuralLLMEngine
except ImportError:
    # Fallback to local import if llm_engine is placed adjacent
    try:
        import llm_engine
        internal_llm = llm_engine.internal_llm
        InternalNeuralLLMEngine = llm_engine.InternalNeuralLLMEngine
    except Exception as e:
        raise ImportError(f"Failed to import llm_engine from {sys.path}: {e}")

__all__ = ["internal_llm", "InternalNeuralLLMEngine"]
