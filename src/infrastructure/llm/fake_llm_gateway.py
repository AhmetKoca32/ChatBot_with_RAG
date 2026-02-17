"""Fake LLM gateway for development (no API key). Replace with real LLM when using RAG/LlamaIndex."""

from src.application.interfaces.llm_gateway import LLMGateway


class FakeLLMGateway(LLMGateway):
    """
    In-memory implementation for development/demo.
    For production, implement LLMGateway with OpenAI/OpenAI-compatible API
    and inject via dependencies.
    """

    def invoke(self, prompt: str, **kwargs: object) -> str:
        return f"[Demo] Alındı: {prompt[:100]}{'...' if len(prompt) > 100 else ''}. RAG (LlamaIndex) bağlandığında gerçek yanıt verilecek."
