"""LLM service implementations (LlamaIndex / RAG compatible)."""

from src.infrastructure.llm.deepseek_llm_gateway import DeepSeekLLMGateway
from src.infrastructure.llm.fake_llm_gateway import FakeLLMGateway

__all__ = ["DeepSeekLLMGateway", "FakeLLMGateway"]
