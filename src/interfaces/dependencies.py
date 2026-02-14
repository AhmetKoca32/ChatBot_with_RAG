"""Dependency Injection: FastAPI Depends and factory functions."""

from fastapi import Depends

from src.application.interfaces.llm_gateway import LLMGateway
from src.application.use_cases.hello_agent import HelloAgentUseCase
from src.infrastructure.llm.fake_llm_gateway import FakeLLMGateway


def get_llm_gateway() -> LLMGateway:
    """Provide LLM gateway implementation. Swap for real LLM (e.g. OpenAI) via env."""
    return FakeLLMGateway()


def get_hello_agent_use_case(
    llm_gateway: LLMGateway = Depends(get_llm_gateway),
) -> HelloAgentUseCase:
    """Hello Agent use case with injected LLMGateway."""
    return HelloAgentUseCase(llm_gateway=llm_gateway)
