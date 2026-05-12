"""Preprocess the raw SHL catalog into normalized searchable records."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.catalog import make_search_text  # noqa: E402


RAW_PATH = ROOT / "data" / "catalog.json"
OUTPUT_PATH = ROOT / "data" / "processed_catalog.json"


def preprocess_catalog(raw_path: Path = RAW_PATH, output_path: Path = OUTPUT_PATH) -> list[dict]:
    """Normalize catalog data and add search_text."""
    with raw_path.open("r", encoding="utf-8") as file:
        items = json.load(file)
    processed: list[dict] = []
    seen_urls: set[str] = set()
    for item in items:
        url = str(item.get("link", "")).strip()
        name = str(item.get("name", "")).strip()
        if not name or not url or url in seen_urls:
            continue
        seen_urls.add(url)
        normalized = dict(item)
        normalized["name"] = name
        normalized["link"] = url
        normalized["job_levels"] = list(item.get("job_levels") or [])
        normalized["keys"] = list(item.get("keys") or [])
        normalized["languages"] = list(item.get("languages") or [])
        normalized["description"] = str(item.get("description", "")).strip()
        normalized["search_text"] = make_search_text(normalized)
        processed.append(normalized)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(processed, file, indent=2, ensure_ascii=False)
    return processed


if __name__ == "__main__":
    records = preprocess_catalog()
    print(f"Processed {len(records)} catalog records -> {OUTPUT_PATH}")
