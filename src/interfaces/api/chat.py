"""Chat API routes (RAG chatbot — LlamaIndex will add retrieval)."""

from fastapi import APIRouter, Depends

from src.application.use_cases.chat import ChatUseCase
from src.interfaces.schemas.chat import ChatRequest, ChatResponseSchema
from src.interfaces.dependencies import get_chat_use_case

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponseSchema)
def chat(
    body: ChatRequest,
    use_case: ChatUseCase = Depends(get_chat_use_case),
) -> ChatResponseSchema:
    """Send a message and get a response (RAG will be added via LlamaIndex)."""
    response = use_case.run(body.message)
    return ChatResponseSchema(response=response, success=True, sources=[])
