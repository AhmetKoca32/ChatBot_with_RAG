"""
Chroma vector store adapter (Infrastructure).
Clean Architecture: vector persistence bu katmanda; RAG modülü bunu kullanır.
"""

import os
from pathlib import Path

import chromadb


def get_chroma_collection(
    *,
    persist_dir: str | None = None,
    collection_name: str = "rag_chatbot",
) -> chromadb.Collection:
    """
    Chroma persistent client ve koleksiyon döndürür.
    persist_dir yoksa CHROMA_PERSIST_DIR env, default ./data/chroma.
    """
    path = persist_dir or os.getenv("CHROMA_PERSIST_DIR", "./data/chroma")
    Path(path).mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=path)
    return client.get_or_create_collection(
        name=collection_name,
        metadata={"description": "RAG chatbot documents"},
    )
