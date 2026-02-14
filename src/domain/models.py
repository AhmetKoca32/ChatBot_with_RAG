"""Domain models and value objects with Pydantic validation."""

from pydantic import BaseModel, Field


class AgentState(BaseModel):
    """State passed through LangGraph agent nodes. Validated with Pydantic."""
    messages: list[dict[str, str]] = Field(default_factory=list, description="Conversation messages")
    current_input: str = Field(default="", description="Latest user input")
    response: str = Field(default="", description="Agent response to return")

    model_config = {"extra": "allow"}  # LangGraph may add keys
