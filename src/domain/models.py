"""Domain models and value objects with Pydantic validation."""

from pydantic import BaseModel, Field


class ChatResponse(BaseModel):
    """Result of a chat turn (RAG-ready: sources can be added later)."""
    response: str = Field(..., description="Model response text")
    sources: list[str] = Field(default_factory=list, description="Optional source refs for RAG")
