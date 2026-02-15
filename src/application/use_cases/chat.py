"""Use case: chat with LLM (RAG will be added via LlamaIndex later)."""

from src.application.interfaces.llm_gateway import LLMGateway


class ChatUseCase:
    """Send user message to LLM and return response. No agent graph."""

    def __init__(self, llm_gateway: LLMGateway) -> None:
        self._llm_gateway = llm_gateway

    def run(self, user_message: str) -> str:
        """Get LLM response for the given message."""
        if not user_message.strip():
            return "Lütfen bir mesaj yazın."
        return self._llm_gateway.invoke(user_message.strip())
