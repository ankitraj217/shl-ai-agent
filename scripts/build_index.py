"""Build the FAISS semantic search index for the processed catalog."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.embeddings import encode_texts  # noqa: E402
from scripts.preprocess import OUTPUT_PATH, preprocess_catalog  # noqa: E402


INDEX_PATH = ROOT / "data" / "faiss.index"
METADATA_PATH = ROOT / "data" / "index_metadata.json"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def build_index() -> None:
    """Encode catalog records and persist a FAISS inner-product index."""
    import faiss

    if not OUTPUT_PATH.exists():
        preprocess_catalog()
    with OUTPUT_PATH.open("r", encoding="utf-8") as file:
        items = json.load(file)
    texts = [item["search_text"] for item in items]
    vectors, backend, dimension = encode_texts(texts, MODEL_NAME)
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    faiss.write_index(index, str(INDEX_PATH))
    metadata = {
        "embedding_model": MODEL_NAME,
        "embedding_backend": backend,
        "dimension": dimension,
        "count": len(items),
        "items": [{"entity_id": item["entity_id"], "name": item["name"]} for item in items],
    }
    with METADATA_PATH.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2)
    print(f"Built FAISS index with {len(items)} vectors -> {INDEX_PATH}")


if __name__ == "__main__":
    build_index()
