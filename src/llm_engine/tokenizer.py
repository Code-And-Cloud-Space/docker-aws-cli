import re
from typing import List

class InternalTokenizer:
    """
    Deterministic sub-word & lexical tokenizer for natural language queries.
    Cleans punctuation, strips stop-words, and extracts n-grams for attention scoring.
    """
    STOP_WORDS = {
        "a", "an", "the", "in", "on", "at", "by", "for", "with", "about",
        "against", "between", "into", "through", "during", "before", "after",
        "above", "below", "to", "from", "up", "down", "is", "are", "was",
        "were", "be", "been", "being", "have", "has", "had", "do", "does",
        "did", "but", "if", "or", "because", "as", "until", "while", "of"
    }

    def tokenize(self, text: str) -> List[str]:
        cleaned = re.sub(r'[^a-zA-Z0-9\s><=\$\.,_-]', ' ', text.lower())
        tokens = [t.strip() for t in cleaned.split() if t.strip()]
        return tokens

    def extract_ngrams(self, tokens: List[str], max_n: int = 3) -> List[str]:
        ngrams = []
        n_tokens = len(tokens)
        for n in range(1, max_n + 1):
            for i in range(n_tokens - n + 1):
                ngrams.append(" ".join(tokens[i:i + n]))
        return ngrams
