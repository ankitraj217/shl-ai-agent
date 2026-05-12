"""FastAPI application entry point."""

from fastapi import FastAPI

from app.routes.chat import router as chat_router
from app.utils.logging import configure_logging


configure_logging()

app = FastAPI(
    title="SHL Conversational Assessment Recommender",
    version="1.0.0",
    description="Stateless conversational RAG API for SHL assessment recommendations.",
)

app.include_router(chat_router)

