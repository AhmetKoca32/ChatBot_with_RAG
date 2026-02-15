"""Port: RAG index / retrieval — abstract interface for document index and query."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class RetrievedChunk:
    """One chunk returned from RAG retrieval."""
    text: str
    source: str = ""  # e.g. file name
    score: float = 0.0


class RAGGateway(ABC):
    """
    Abstract interface for RAG: index documents and retrieve relevant chunks.
    Implement in infrastructure with LlamaIndex + Chroma + sentence-transformers.
    """

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        """Return top_k most relevant chunks for the query."""
        ...

    @abstractmethod
    def index_directory(self, directory_path: str) -> int:
        """
        Load documents from directory (PDF, txt, etc.), chunk, embed, store.
        Returns number of chunks indexed.
        """
        ...
