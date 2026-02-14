"""Port: LLM gateway - abstract interface for LangChain/LangGraph compatible LLM."""

from abc import ABC, abstractmethod


class LLMGateway(ABC):
    """Abstract interface for LLM invocations. Implement in infrastructure."""

    @abstractmethod
    def invoke(self, prompt: str, **kwargs: object) -> str:
        """Invoke LLM with prompt and return text response."""
        ...
