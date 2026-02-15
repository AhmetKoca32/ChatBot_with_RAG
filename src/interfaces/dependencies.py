"""Dependency Injection: FastAPI Depends and factory functions."""

from fastapi import Depends

from src.application.interfaces.llm_gateway import LLMGateway
from src.application.use_cases.chat import ChatUseCase
from src.infrastructure.llm.fake_llm_gateway import FakeLLMGateway


def get_llm_gateway() -> LLMGateway:
    """Provide LLM gateway implementation. Swap for real LLM (e.g. OpenAI) via env."""
    return FakeLLMGateway()


def get_chat_use_case(
    llm_gateway: LLMGateway = Depends(get_llm_gateway),
) -> ChatUseCase:
    """Chat use case with injected LLMGateway. RAG (LlamaIndex) will be wired here later."""
    return ChatUseCase(llm_gateway=llm_gateway)
