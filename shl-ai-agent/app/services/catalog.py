"""Catalog loading and normalization."""

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from app.models.catalog import Assessment
from app.utils.config import get_settings


def make_search_text(item: dict[str, Any]) -> str:
    """Create searchable text from catalog fields."""
    parts: list[str] = [
        str(item.get("name", "")),
        str(item.get("description", "")),
        " ".join(item.get("job_levels") or []),
        " ".join(item.get("keys") or []),
        str(item.get("duration", "")),
    ]
    return " ".join(part for part in parts if part).strip()


def normalize_item(item: dict[str, Any]) -> Assessment:
    """Normalize one raw catalog item."""
    search_text = item.get("search_text") or make_search_text(item)
    return Assessment(
        entity_id=str(item.get("entity_id", "")),
        name=str(item.get("name", "")).strip(),
        url=str(item.get("link") or item.get("url") or "").strip(),
        description=str(item.get("description", "")).strip(),
        job_levels=list(item.get("job_levels") or []),
        categories=list(item.get("keys") or item.get("categories") or []),
        languages=list(item.get("languages") or []),
        duration=str(item.get("duration", "")).strip(),
        remote=str(item.get("remote", "")).strip(),
        adaptive=str(item.get("adaptive", "")).strip(),
        search_text=search_text,
    )


@lru_cache(maxsize=1)
def load_catalog() -> list[Assessment]:
    """Load catalog records from disk."""
    settings = get_settings()
    path = Path(settings.processed_catalog_path)
    if not path.exists():
        path = Path(settings.catalog_path)
    with path.open("r", encoding="utf-8") as file:
        raw_items = json.load(file)
    assessments = [normalize_item(item) for item in raw_items if item.get("name") and (item.get("link") or item.get("url"))]
    if not assessments:
        raise ValueError("catalog is empty or invalid")
    return assessments


def allowed_urls() -> set[str]:
    """Return the set of valid catalog URLs."""
    return {assessment.url for assessment in load_catalog()}
