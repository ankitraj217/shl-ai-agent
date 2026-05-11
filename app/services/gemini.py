"""Gemini integration with safe local fallback."""

import logging

from app.utils.config import get_settings

logger = logging.getLogger(__name__)


class GeminiClient:
    """Thin wrapper around Gemini text generation."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._model = None
        if self.settings.gemini_api_key:
            try:
                import google.generativeai as genai

                genai.configure(api_key=self.settings.gemini_api_key)
                self._model = genai.GenerativeModel(self.settings.gemini_model)
            except Exception as exc:
                logger.warning("Gemini initialization failed: %s", exc)

    @property
    def enabled(self) -> bool:
        """Return whether Gemini is configured."""
        return self._model is not None

    def generate(self, prompt: str) -> str | None:
        """Generate a response, returning None on provider errors."""
        if not self._model:
            return None
        try:
            response = self._model.generate_content(
                prompt,
                generation_config={"temperature": 0.2, "max_output_tokens": 700},
            )
            text = getattr(response, "text", None)
            return text.strip() if text else None
        except Exception as exc:
            logger.warning("Gemini generation failed: %s", exc)
            return None
