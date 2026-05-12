"""Hybrid semantic and keyword retrieval over the SHL catalog."""

from dataclasses import dataclass
import json
import logging
from pathlib import Path
import re

import numpy as np
from rapidfuzz import fuzz

from app.models.catalog import Assessment
from app.services.catalog import load_catalog
from app.services.embeddings import hash_embed
from app.utils.config import get_settings

logger = logging.getLogger(__name__)

SKILL_TERMS = {
    ".net", "android", "angular", "aws", "azure", "c#", "c++", "css", "excel", "html",
    "java", "javascript", "kotlin", "linux", "mysql", "oracle", "php", "python", "react",
    "salesforce", "sap", "sql", "typescript", "unix",
}


@dataclass(frozen=True)
class SearchResult:
    """A scored retrieval result."""

    assessment: Assessment
    score: float


class HybridRetriever:
    """Retrieve assessments using FAISS semantic search plus RapidFuzz keyword scores."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.catalog = load_catalog()
        self._faiss = None
        self._index = None
        self._model = None
        self._embedding_backend = ""
        self._metadata_ids: list[str] = []
        self._by_id = {assessment.entity_id: assessment for assessment in self.catalog}
        self._load_index()

    def _load_index(self) -> None:
        """Load FAISS index and metadata if available."""
        index_path = Path(self.settings.faiss_index_path)
        metadata_path = Path(self.settings.index_metadata_path)
        if not index_path.exists() or not metadata_path.exists():
            logger.warning("FAISS index files are missing; keyword-only retrieval will be used.")
            return
        try:
            import faiss

            self._faiss = faiss
            self._index = faiss.read_index(str(index_path))
            with metadata_path.open("r", encoding="utf-8") as file:
                metadata = json.load(file)
            self._metadata_ids = [str(item["entity_id"]) for item in metadata["items"]]
            self._embedding_backend = metadata.get("embedding_backend", "sentence-transformers")
            if self._embedding_backend == "sentence-transformers":
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(self.settings.embedding_model)
        except Exception as exc:
            logger.warning("Unable to load semantic retriever: %s", exc)
            self._faiss = None
            self._index = None
            self._model = None

    def search(self, query: str, top_k: int = 10) -> list[SearchResult]:
        """Return top matching assessments."""
        query = query.strip()
        if not query:
            return []
        semantic_scores = self._semantic_scores(query, limit=max(top_k * 4, 25))
        query_skills = self._query_skills(query)
        scored: list[SearchResult] = []
        for assessment in self.catalog:
            keyword = self._keyword_score(query, assessment)
            semantic = semantic_scores.get(assessment.entity_id, 0.0)
            combined = (0.62 * semantic) + (0.38 * keyword) if semantic_scores else keyword
            combined = self._apply_skill_guard(combined, query_skills, assessment)
            if combined > 0:
                scored.append(SearchResult(assessment=assessment, score=combined))
        scored.sort(key=lambda result: result.score, reverse=True)
        if query_skills:
            skill_matched = [
                result for result in scored
                if self._assessment_has_skill(result.assessment, query_skills)
            ]
            if skill_matched:
                return skill_matched[:top_k]
        return scored[:top_k]

    def _keyword_score(self, query: str, assessment: Assessment) -> float:
        """Score direct lexical overlap without letting long text swamp product names."""
        lowered_query = query.lower()
        lowered_name = assessment.name.lower()
        lowered_text = assessment.search_text.lower()
        query_tokens = set(re.findall(r"[a-z0-9+#.]{2,}", lowered_query))
        name_tokens = set(re.findall(r"[a-z0-9+#.]{2,}", lowered_name))
        text_tokens = set(re.findall(r"[a-z0-9+#.]{2,}", lowered_text))
        name_ratio = fuzz.token_set_ratio(lowered_query, lowered_name) / 100.0
        text_ratio = fuzz.token_set_ratio(lowered_query, lowered_text) / 100.0
        overlap = len(query_tokens & text_tokens) / max(1, len(query_tokens))
        name_overlap = len(query_tokens & name_tokens) / max(1, len(query_tokens))
        return min(1.0, (0.45 * name_ratio) + (0.25 * text_ratio) + (0.2 * overlap) + (0.1 * name_overlap))

    def _query_skills(self, query: str) -> set[str]:
        """Extract explicit skill terms from a query."""
        lowered = query.lower()
        return {skill for skill in SKILL_TERMS if re.search(rf"(?<![a-z0-9+#.]){re.escape(skill)}(?![a-z0-9+#.])", lowered)}

    def _apply_skill_guard(self, score: float, query_skills: set[str], assessment: Assessment) -> float:
        """Keep explicit skill constraints dominant in the final rank."""
        if not query_skills:
            return score
        lowered_text = assessment.search_text.lower()
        lowered_name = assessment.name.lower()
        if any(self._contains_skill(lowered_name, skill) for skill in query_skills):
            return min(1.0, score + 0.12)
        if any(self._contains_skill(lowered_text, skill) for skill in query_skills):
            return min(1.0, score + 0.04)
        return score * 0.55

    def _assessment_has_skill(self, assessment: Assessment, query_skills: set[str]) -> bool:
        """Return whether an assessment contains one of the requested skills."""
        lowered = assessment.search_text.lower()
        return any(self._contains_skill(lowered, skill) for skill in query_skills)

    def _contains_skill(self, text: str, skill: str) -> bool:
        """Match a skill as a standalone token."""
        return bool(re.search(rf"(?<![a-z0-9+#.]){re.escape(skill)}(?![a-z0-9+#.])", text))

    def _semantic_scores(self, query: str, limit: int) -> dict[str, float]:
        """Return normalized semantic scores from FAISS."""
        if self._index is None:
            return {}
        if self._embedding_backend == "hashing-fallback":
            vector = np.asarray([hash_embed(query)], dtype="float32")
        elif self._model is not None:
            embedding = self._model.encode([query], normalize_embeddings=True, convert_to_numpy=True)
            vector = np.asarray(embedding, dtype="float32")
        else:
            return {}
        distances, indices = self._index.search(vector, min(limit, len(self._metadata_ids)))
        scores: dict[str, float] = {}
        for distance, index in zip(distances[0], indices[0], strict=False):
            if index < 0 or index >= len(self._metadata_ids):
                continue
            entity_id = self._metadata_ids[int(index)]
            scores[entity_id] = max(0.0, min(1.0, float((distance + 1.0) / 2.0)))
        return scores
