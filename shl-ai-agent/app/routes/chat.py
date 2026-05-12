"""HTTP routes for health checks and chat recommendations."""

from fastapi import APIRouter, HTTPException

from app.models.chat import ChatRequest, ChatResponse, HealthResponse
from app.services.conversation import ConversationService

router = APIRouter()
conversation_service = ConversationService()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Return application health."""
    return HealthResponse(status="ok")


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Handle a stateless conversational turn."""
    try:
        return conversation_service.respond(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unable to process chat request.") from exc

