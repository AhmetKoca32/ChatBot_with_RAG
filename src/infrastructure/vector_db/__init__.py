"""Vector DB adapters (Infrastructure). Chroma implementasyonu."""

from src.infrastructure.vector_db.chroma_store import get_chroma_collection

__all__ = ["get_chroma_collection"]
