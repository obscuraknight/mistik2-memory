"""Deterministic hashed character features, not learned semantic embeddings.

These lexical vectors support reciprocal-rank fusion without a model dependency.
Supply an external embed_fn when learned semantic representations are required.
"""
from __future__ import annotations

import hashlib
import math
from typing import Sequence

DIM = 256
NGRAM = 4


def _ngrams(text: str, n: int = NGRAM):
    folded = " ".join((text or "").casefold().split())
    if len(folded) < n:
        yield folded
        return
    for i in range(len(folded) - n + 1):
        yield folded[i:i + n]


def _hash_index(gram: str) -> int:
    digest = hashlib.blake2b(gram.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "little") % DIM


def embed_text(text: str) -> list[float]:
    vector = [0.0] * DIM
    for gram in _ngrams(text):
        vector[_hash_index(gram)] += 1.0
    norm = math.sqrt(sum(x * x for x in vector)) or 1.0
    return [x / norm for x in vector]


def hashed_embed_fn(texts: Sequence[str]) -> list[list[float]]:
    """Drop-in ``Retriever(embed_fn=...)`` implementation."""
    return [embed_text(text) for text in texts]
