"""
RAG adapter (Infrastructure): Application port RAGGateway implementasyonu.
LlamaIndex (chunking, embedding, index) + Vector DB (Chroma) kullanır.
PDF metni pypdf ile çıkarılır.
"""

import os
import re
from pathlib import Path

from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import Document
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from pypdf import PdfReader

from src.application.interfaces.rag_gateway import RAGGateway, RetrievedChunk
from src.infrastructure.vector_db import get_chroma_collection

# Sabit chunking: 512 karakter, 50 overlap
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50 # kompleks işlerde daha da arttırılabilir 
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
CHROMA_COLLECTION = "rag_chatbot"


class LlamaChromaRAG(RAGGateway):
    """
    RAG: LlamaIndex + HuggingFace embedding; vector persistence Vector DB katmanından.
    PDF/txt pypdf ve dosya okuma ile yüklenir; SentenceSplitter ile chunk'lanır.
    """

    def __init__(self, persist_dir: str | None = None) -> None:
        self._persist_dir = persist_dir or os.getenv("CHROMA_PERSIST_DIR", "./data/chroma")
        self._collection = get_chroma_collection(
            persist_dir=self._persist_dir,
            collection_name=CHROMA_COLLECTION,
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

    def get_doc_start_chunks(self) -> list[RetrievedChunk]:
        """Her dokümanın başındaki chunk'ları döndür (doc_start=1; index'te ilk 12 chunk/doc)."""
        try:
            result = self._collection.get(
                where={"doc_start": "1"},
                include=["metadatas", "documents"],
                limit=500,
            )
        except Exception:
            return []
        if not result or not result.get("documents"):
            return []
        metadatas = result["metadatas"] or []
        documents = result["documents"] or []
        items = [
            (m.get("chunk_index", 999), m.get("file_path", ""), doc)
            for m, doc in zip(metadatas, documents)
        ]
        items.sort(key=lambda x: (x[1], x[0]))
        return [
            RetrievedChunk(text=doc, source=path, score=1.0)
            for _, path, doc in items
        ]

    def _normalize_pdf_text(self, text: str) -> str:
        """PDF'den 'P a z a r t e s i', '1 . 5 0 0 T L' gibi harf/rakam arası boşlukları düzelt."""
        return re.sub(r"(?<=[\w.]) (?=[\w.])", "", text)

    def _load_documents_from_dir(self, dir_path: Path) -> list[Document]:
        """PDF'den pypdf ile metin çıkar; .txt'yi oku. Ham PDF okumayı önler."""
        documents: list[Document] = []
        for f in sorted(dir_path.iterdir()):
            if f.suffix.lower() == ".pdf":
                try:
                    reader = PdfReader(str(f))
                    text_parts = []
                    for page in reader.pages:
                        t = page.extract_text()
                        if t:
                            text_parts.append(t)
                    if text_parts:
                        text = "\n".join(text_parts)
                        text = self._normalize_pdf_text(text)
                        documents.append(
                            Document(text=text, metadata={"file_path": str(f), "filename": f.name})
                        )
                except Exception:
                    continue
            elif f.suffix.lower() == ".txt":
                try:
                    text = f.read_text(encoding="utf-8", errors="replace")
                    if text.strip():
                        documents.append(
                            Document(text=text, metadata={"file_path": str(f), "filename": f.name})
                        )
                except Exception:
                    continue
        return documents

    def index_directory(self, directory_path: str) -> int:
        """Load docs from directory, chunk, embed, store. Returns number of chunks."""
        path = Path(directory_path)
        if not path.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory_path}")
        # Eski kayıtları temizle; aksi halde re-index eski chunk'ları da bırakır (tag/metadata yok)
        try:
            existing = self._collection.get(include=[], limit=10_000)
            if existing.get("ids"):
                self._collection.delete(ids=existing["ids"])
        except Exception:
            pass
        documents = self._load_documents_from_dir(path)
        if not documents:
            return 0
        nodes = self._splitter.get_nodes_from_documents(documents)
        # Chunk sırası; doc_start = her doc'ın ilk chunk'ları (genel kural: kurallar/fiyat/program hepsi başta)
        file_counter: dict[str, int] = {}
        for node in nodes:
            fp = node.metadata.get("file_path", node.metadata.get("filename", ""))
            idx = file_counter.get(fp, 0)
            file_counter[fp] = idx + 1
            node.metadata["chunk_index"] = idx
            node.metadata["doc_start"] = "1" if idx < 12 else "0"
        self._index = VectorStoreIndex(
            nodes,
            storage_context=self._storage_context,
            embed_model=self._embed_model,
        )
        return len(nodes)
