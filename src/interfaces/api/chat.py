"""Chat API routes (RAG chatbot — LlamaIndex retrieval + LLM)."""

from fastapi import APIRouter, Depends

from src.application.use_cases.chat import ChatUseCase, RAG_TOP_K
from src.interfaces.dependencies import get_chat_use_case, get_rag_gateway
from src.interfaces.schemas.chat import ChatRequest, ChatResponseSchema

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponseSchema)
def chat(
    body: ChatRequest,
    use_case: ChatUseCase = Depends(get_chat_use_case),
) -> ChatResponseSchema:
    """Send a message and get a RAG-augmented response with optional sources."""
    result = use_case.run(body.message)
    return ChatResponseSchema(
        response=result.response,
        success=True,
        sources=result.sources,
    )


@router.get("/debug")
def chat_debug(
    q: str = "salon kaçta açılıyor",
    rag_gateway=Depends(get_rag_gateway),
) -> dict:
    """
    RAG context'in ne döndüğünü kontrol et: doc_start dolu mu, context'te saat var mı?
    Sorun tespiti için; production'da kapatılabilir.
    """
    chunks = rag_gateway.retrieve(q, top_k=RAG_TOP_K)
    seen = {c.text[:80] for c in chunks}
    doc_starts = getattr(rag_gateway, "get_doc_start_chunks", lambda: [])()
    prepend = [c for c in doc_starts if c.text[:80] not in seen]
    for c in prepend:
        seen.add(c.text[:80])
    chunks = prepend + chunks
    context = "\n\n".join(c.text for c in chunks) if chunks else ""
    return {
        "doc_start_count": len(doc_starts),
        "semantic_count": RAG_TOP_K,
        "total_chunks": len(chunks),
        "context_contains_07": "07:00" in context or "07:00" in context.replace(" ", ""),
        "context_contains_Pazartesi": "Pazartesi" in context,
        "context_preview": context[:2500],
    }
