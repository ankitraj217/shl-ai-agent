"""Embedding helpers for semantic indexing.

The preferred production path uses sentence-transformers. A deterministic
hashing fallback keeps local verification runnable on Python versions where
the PyTorch wheel stack is unavailable.
"""

from __future__ import annotations

import hashlib
import logging
import re

import numpy as np

logger = logging.getLogger(__name__)

FALLBACK_DIMENSION = 384


def encode_texts(texts: list[str], model_name: str) -> tuple[np.ndarray, str, int]:
    """Encode texts and return vectors, backend name, and dimension."""
    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(model_name)
        embeddings = model.encode(texts, normalize_embeddings=True, batch_size=32, show_progress_bar=True)
        vectors = np.asarray(embeddings, dtype="float32")
        return vectors, "sentence-transformers", vectors.shape[1]
    except Exception as exc:
        logger.warning("Falling back to hashing embeddings because sentence-transformers is unavailable: %s", exc)
        vectors = np.vstack([hash_embed(text) for text in texts]).astype("float32")
        return vectors, "hashing-fallback", FALLBACK_DIMENSION


def hash_embed(text: str, dimension: int = FALLBACK_DIMENSION) -> np.ndarray:
    """Create a deterministic normalized bag-of-tokens embedding."""
    vector = np.zeros(dimension, dtype="float32")
    tokens = re.findall(r"[a-zA-Z0-9+#.]{2,}", text.lower())
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        index = int.from_bytes(digest[:4], "little") % dimension
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += sign
    norm = float(np.linalg.norm(vector))
    if norm:
        vector /= norm
    return vector
