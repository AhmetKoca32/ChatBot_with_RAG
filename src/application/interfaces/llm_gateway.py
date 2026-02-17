"""Port: LLM gateway - abstract interface for LLM (e.g. OpenAI, used with LlamaIndex RAG)."""

from abc import ABC, abstractmethod


class LLMGateway(ABC):
    """Abstract interface for LLM invocations. Implement in infrastructure."""

    @abstractmethod
    def invoke(self, prompt: str, **kwargs: object) -> str:
        """Invoke LLM with prompt and return text response."""
        ...
