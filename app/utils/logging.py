"""Logging setup."""

import logging

from app.utils.config import get_settings


def configure_logging() -> None:
    """Configure standard application logging."""
    settings = get_settings()
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
