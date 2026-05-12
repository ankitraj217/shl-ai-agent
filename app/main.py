"""FastAPI application entry point."""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.routes.chat import router as chat_router
from app.utils.logging import configure_logging


configure_logging()

app = FastAPI(
    title="SHL Conversational Assessment Recommender",
    version="1.0.0",
    description="Stateless conversational RAG API for SHL assessment recommendations.",
)

app.include_router(chat_router)

FRONTEND_DIST = Path(__file__).resolve().parents[1] / "frontend" / "dist"
FRONTEND_INDEX = FRONTEND_DIST / "index.html"
FRONTEND_ASSETS = FRONTEND_DIST / "assets"
RESERVED_PATHS = {"chat", "health", "docs", "redoc", "openapi.json"}

app.mount(
    "/assets",
    StaticFiles(directory=FRONTEND_ASSETS, check_dir=False),
    name="frontend-assets",
)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def serve_frontend() -> FileResponse:
    """Serve the compiled React application."""
    if not FRONTEND_INDEX.exists():
        raise HTTPException(
            status_code=404,
            detail="Frontend build not found. Run npm run build in frontend/.",
        )
    return FileResponse(FRONTEND_INDEX)


@app.get("/{full_path:path}", response_class=HTMLResponse, include_in_schema=False)
def serve_spa_fallback(full_path: str) -> FileResponse:
    """Serve React routes while preserving API and documentation paths."""
    first_segment = full_path.split("/", 1)[0]
    if first_segment in RESERVED_PATHS:
        raise HTTPException(status_code=404, detail="Not found")

    requested_file = (FRONTEND_DIST / full_path).resolve()
    if requested_file.is_file() and FRONTEND_DIST in requested_file.parents:
        return FileResponse(requested_file)

    if not FRONTEND_INDEX.exists():
        raise HTTPException(
            status_code=404,
            detail="Frontend build not found. Run npm run build in frontend/.",
        )
    return FileResponse(FRONTEND_INDEX)
