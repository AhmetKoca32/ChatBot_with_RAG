"""
Infrastructure: dış dünya adaptörleri (Clean Architecture).
- llm: LLMGateway implementasyonları (Fake, DeepSeek)
- rag: RAGGateway implementasyonu (LlamaChromaRAG); doküman yükleme, chunking, retrieval
- vector_db: vektör kalıcılığı (Chroma); RAG tarafından kullanılır
"""

from src.infrastructure.llm.fake_llm_gateway import FakeLLMGateway

__all__ = ["FakeLLMGateway"]
