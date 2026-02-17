"""Use case: chat with LLM and RAG context (LlamaIndex retrieval)."""

from src.application.interfaces.llm_gateway import LLMGateway
from src.application.interfaces.rag_gateway import RAGGateway
from src.domain.models import ChatResponse

RAG_TOP_K = 14

class ChatUseCase:
    """Send user message to LLM with RAG context and return response + sources."""

    def __init__(
        self,
        llm_gateway: LLMGateway,
        rag_gateway: RAGGateway,
    ) -> None:
        self._llm_gateway = llm_gateway
        self._rag_gateway = rag_gateway

    def run(self, user_message: str) -> ChatResponse:
        """Get LLM response using RAG-retrieved context; return response and sources."""
        if not user_message.strip():
            return ChatResponse(response="Lütfen bir mesaj yazın.", sources=[])

        query = user_message.strip()
        chunks = self._rag_gateway.retrieve(query, top_k=RAG_TOP_K)
        seen = {c.text[:80] for c in chunks}
        # Her dokümanın başından chunk'lar (doc_start; tek kural)
        doc_starts = getattr(self._rag_gateway, "get_doc_start_chunks", lambda: [])()
        prepend = [c for c in doc_starts if c.text[:80] not in seen]
        for c in prepend:
            seen.add(c.text[:80])
        chunks = prepend + chunks

        context = (
            "\n\n".join(c.text for c in chunks) if chunks else "(İlgili bağlam bulunamadı.)"
        )
        sources = list(
            dict.fromkeys(c.source for c in chunks if c.source)
        )  # unique, order preserved

        prompt = (
            "Şu bağlamı kullanarak kullanıcının sorusunu yanıtla.\n"
            "Kurallar: Bağlamdaki saat, fiyat, kural, program vb. bilgiyi doğrudan kullanıp net cevap ver. "
            "Cevabında bu bilgileri yazdıysan 'bağlamda yok', 'iletişime geçin' veya 'kesin bilgi için...' deme; verdiğin bilgi yeterli. "
            "Bağlamda gerçekten ilgili bilgi yoksa kısaca bilmediğini söyle.\n\n"
            f"Bağlam:\n{context}\n\nKullanıcı: {query}"
        )
        response_text = self._llm_gateway.invoke(prompt)
        return ChatResponse(response=response_text, sources=sources)
