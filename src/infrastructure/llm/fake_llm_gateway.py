"""Fake LLM gateway for Hello Agent (no API key). Replace with LangChain ChatOpenAI in production."""

from src.application.interfaces.llm_gateway import LLMGateway


class FakeLLMGateway(LLMGateway):
    """
    In-memory implementation for development/demo.
    For production, implement LLMGateway using langchain_community.chat_models.ChatOpenAI
    or similar and inject API key via settings.
    """

    def invoke(self, prompt: str, **kwargs: object) -> str:
        # Simple greeting logic so Hello Agent works without an LLM
        if "greeting" in prompt.lower() or "name" in prompt.lower():
            name = "World"
            parts = prompt.replace(".", " ").replace(":", " ").split()
            skip = ("generate", "short", "friendly", "greeting", "for", "the", "name", "reply", "with", "only", "no", "quotes")
            for part in parts:
                word = part.strip(".,;").strip()
                if word and word.isalpha() and word.lower() not in skip:
                    name = word
                    break
            return f"Hello, {name}!"
        return "Hello from Agent!"
