"""DeepSeek LLM gateway (OpenAI-compatible API)."""

import os

from openai import OpenAI

from src.application.interfaces.llm_gateway import LLMGateway

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"


class DeepSeekLLMGateway(LLMGateway):
    """
    LLM via DeepSeek API (OpenAI-compatible).
    Uses DEEPSEEK_API_KEY from env; optional DEEPSEEK_MODEL, DEEPSEEK_BASE_URL.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        self._api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self._base_url = base_url or os.getenv("DEEPSEEK_BASE_URL", DEEPSEEK_BASE_URL)
        self._model = model or os.getenv("DEEPSEEK_MODEL", DEEPSEEK_MODEL)
        self._client = OpenAI(api_key=self._api_key, base_url=self._base_url)

    def invoke(self, prompt: str, **kwargs: object) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
        )
        if not response.choices:
            return ""
        return response.choices[0].message.content or ""
