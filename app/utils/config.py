"""Application configuration."""

from functools import lru_cache
import os

from dotenv import load_dotenv
from pydantic import BaseModel


load_dotenv()


class Settings(BaseModel):
    """Environment-driven application settings."""

    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    catalog_path: str = os.getenv("CATALOG_PATH", "data/catalog.json")
    processed_catalog_path: str = os.getenv("PROCESSED_CATALOG_PATH", "data/processed_catalog.json")
    faiss_index_path: str = os.getenv("FAISS_INDEX_PATH", "data/faiss.index")
    index_metadata_path: str = os.getenv("INDEX_METADATA_PATH", "data/index_metadata.json")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings."""
    return Settings()
