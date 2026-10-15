import math
from typing import Dict, List, Tuple

class InternalEmbeddingSpace:
    """
    In-process dense semantic vector space with precomputed prototype vectors
    representing CRM entities, relationships, attributes, and operators.
    Zero external neural network or GPU dependencies.
    """
    DIM = 8

    PROTOTYPES = {
        # Entity prototypes
        "Account": [0.95, 0.10, 0.05, 0.20, 0.15, 0.00, 0.00, 0.85],
        "Contact": [0.10, 0.95, 0.10, 0.15, 0.05, 0.85, 0.10, 0.20],
        "Opportunity": [0.15, 0.10, 0.95, 0.85, 0.20, 0.10, 0.90, 0.30],
        "Lead": [0.20, 0.70, 0.40, 0.10, 0.95, 0.60, 0.30, 0.10],
        
        # Domain prototypes
        "Media": [0.60, 0.40, 0.50, 0.30, 0.20, 0.10, 0.20, 0.70],
        "Technology": [0.70, 0.30, 0.40, 0.60, 0.20, 0.30, 0.50, 0.80],
        
        # Financial prototypes
        "HighRevenue": [0.30, 0.10, 0.90, 0.95, 0.10, 0.10, 0.85, 0.70],
        "ClosedWon": [0.10, 0.10, 0.95, 0.90, 0.10, 0.05, 0.95, 0.20],
    }

    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(b * b for b in v2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    def get_similarity(self, concept1: str, concept2: str) -> float:
        v1 = self.PROTOTYPES.get(concept1)
        v2 = self.PROTOTYPES.get(concept2)
        if not v1 or not v2:
            return 0.0
        return self.cosine_similarity(v1, v2)
