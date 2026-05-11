"""Pydantic schemas for public API contracts."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class HealthResponse(BaseModel):
    """Health endpoint response."""

    status: Literal["ok"]


class Message(BaseModel):
    """A single chat message supplied by the client."""

    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=4000)

    @field_validator("content")
    @classmethod
    def content_must_not_be_blank(cls, value: str) -> str:
        """Reject whitespace-only content."""
        stripped = value.strip()
        if not stripped:
            raise ValueError("message content cannot be blank")
        return stripped


class ChatRequest(BaseModel):
    """Chat request containing stateless conversation history."""

    messages: list[Message] = Field(..., min_length=1, max_length=16)

    @field_validator("messages")
    @classmethod
    def must_contain_user_message(cls, value: list[Message]) -> list[Message]:
        """Ensure there is at least one user message to answer."""
        if not any(message.role == "user" for message in value):
            raise ValueError("at least one user message is required")
        return value


class Recommendation(BaseModel):
    """Assessment recommendation returned to callers."""

    name: str
    url: str
    test_type: str

    model_config = ConfigDict(extra="forbid")


class ChatResponse(BaseModel):
    """Chat response with grounded recommendations."""

    reply: str
    recommendations: list[Recommendation]
    end_of_conversation: bool = False

    model_config = ConfigDict(extra="forbid")
