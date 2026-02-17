"""Dependency Injection: FastAPI Depends and factory functions."""

import os

from fastapi import Depends

from src.application.interfaces.llm_gateway import LLMGateway
from src.application.interfaces.rag_gateway import RAGGateway
from src.application.use_cases.chat import ChatUseCase
from src.infrastructure.llm.deepseek_llm_gateway import DeepSeekLLMGateway
from src.infrastructure.llm.fake_llm_gateway import FakeLLMGateway
from src.infrastructure.rag.llama_chroma_rag import LlamaChromaRAG


def get_llm_gateway() -> LLMGateway:
    """Use DeepSeek when DEEPSEEK_API_KEY is set, otherwise FakeLLMGateway."""
    if os.getenv("DEEPSEEK_API_KEY"):
        return DeepSeekLLMGateway()
    return FakeLLMGateway()


def get_rag_gateway() -> RAGGateway:
    """Provide RAG gateway (LlamaIndex + Chroma). Uses CHROMA_PERSIST_DIR for persistence."""
    return LlamaChromaRAG()


def get_chat_use_case(
    llm_gateway: LLMGateway = Depends(get_llm_gateway),
    rag_gateway: RAGGateway = Depends(get_rag_gateway),
) -> ChatUseCase:
    """Chat use case with injected LLM and RAG gateways."""
    return ChatUseCase(llm_gateway=llm_gateway, rag_gateway=rag_gateway)
