"""
RAG implementation: LlamaIndex + Chroma + sentence-transformers (sabit chunking).
Implements RAGGateway for application layer.
"""

import os
from pathlib import Path

import chromadb
from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

from src.application.interfaces.rag_gateway import RAGGateway, RetrievedChunk

# Sabit chunking: 512 karakter, 50 overlap
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
CHROMA_COLLECTION = "rag_chatbot"


class LlamaChromaRAG(RAGGateway):
    """
    RAG with LlamaIndex, Chroma (persistent), HuggingFace embedding.
    SimpleDirectoryReader for PDF/txt; SentenceSplitter for fixed chunking.
    """

    def __init__(self, persist_dir: str | None = None) -> None:
        self._persist_dir = persist_dir or os.getenv("CHROMA_PERSIST_DIR", "./data/chroma")
        Path(self._persist_dir).mkdir(parents=True, exist_ok=True)
        self._chroma_client = chromadb.PersistentClient(path=self._persist_dir)
        self._collection = self._chroma_client.get_or_create_collection(
            name=CHROMA_COLLECTION,
            metadata={"description": "RAG chatbot documents"},
        )
        self._embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL)
        self._vector_store = ChromaVectorStore(chroma_collection=self._collection)
        self._storage_context = StorageContext.from_defaults(vector_store=self._vector_store)
        self._splitter = SentenceSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
        self._index: VectorStoreIndex | None = None
        self._refresh_index()

    def _refresh_index(self) -> None:
        """Load index from existing vector store (for retrieval after restart)."""
        from llama_index.core import VectorStoreIndex

        self._index = VectorStoreIndex.from_vector_store(
            self._vector_store,
            embed_model=self._embed_model,
        )

    def retrieve(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        """Return top_k most relevant chunks."""
        if self._index is None:
            self._refresh_index()
        retriever = self._index.as_retriever(similarity_top_k=top_k)
        nodes = retriever.retrieve(query)
        return [
            RetrievedChunk(
                text=node.get_content(),
                source=node.metadata.get("file_path", node.metadata.get("filename", "")),
                score=float(node.score) if node.score is not None else 0.0,
            )
            for node in nodes
        ]

    def index_directory(self, directory_path: str) -> int:
        """Load docs from directory, chunk, embed, store. Returns number of chunks."""
        path = Path(directory_path)
        if not path.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory_path}")
        reader = SimpleDirectoryReader(input_dir=str(path))
        documents = reader.load_data()
        if not documents:
            return 0
        nodes = self._splitter.get_nodes_from_documents(documents)
        self._index = VectorStoreIndex(
            nodes,
            storage_context=self._storage_context,
            embed_model=self._embed_model,
        )
        return len(nodes)
