"""Infrastructure: LLM services, Vector DB, tools (search, PDF parser, etc.)."""

from src.infrastructure.llm.fake_llm_gateway import FakeLLMGateway

__all__ = ["FakeLLMGateway"]
