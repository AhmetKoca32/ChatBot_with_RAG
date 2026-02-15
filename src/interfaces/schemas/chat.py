"""Chat API schemas with Pydantic validation."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""

    message: str = Field(..., min_length=1, max_length=2000, description="User message")


class ChatResponseSchema(BaseModel):
    """Response from chat (RAG-ready: sources field for later)."""

    response: str = Field(..., description="Assistant response")
    success: bool = Field(default=True, description="Whether the request succeeded")
    sources: list[str] = Field(default_factory=list, description="Optional source refs (for RAG)")
