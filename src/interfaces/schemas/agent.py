"""Agent API schemas with Pydantic validation."""

from pydantic import BaseModel, Field


class HelloAgentRequest(BaseModel):
    """Request body for Hello Agent endpoint."""

    message: str = Field(default="", min_length=0, max_length=2000, description="User input for the agent")


class HelloAgentResponse(BaseModel):
    """Response from Hello Agent."""

    response: str = Field(..., description="Agent greeting response")
    success: bool = Field(default=True, description="Whether the request succeeded")
