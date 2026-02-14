"""Agent API routes."""

from fastapi import APIRouter, Depends

from src.application.use_cases.hello_agent import HelloAgentUseCase
from src.interfaces.schemas.agent import HelloAgentRequest, HelloAgentResponse
from src.interfaces.dependencies import get_hello_agent_use_case

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/hello", response_model=HelloAgentResponse)
def hello_agent(
    body: HelloAgentRequest,
    use_case: HelloAgentUseCase = Depends(get_hello_agent_use_case),
) -> HelloAgentResponse:
    """Run the Hello Agent flow and return a greeting."""
    response = use_case.run(body.message)
    return HelloAgentResponse(response=response, success=True)
