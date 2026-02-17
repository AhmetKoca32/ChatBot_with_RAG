"""
Index documents into RAG (Chroma). Run from project root.
Usage:
  python scripts/index_docs.py [directory]
  Default directory: data/documents
"""

import sys
from pathlib import Path

# Project root (parent of scripts/)
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.infrastructure.rag.llama_chroma_rag import LlamaChromaRAG


def main() -> None:
    directory = sys.argv[1] if len(sys.argv) > 1 else "data/documents"
    path = Path(directory)
    if not path.is_absolute():
        path = ROOT / path
    if not path.is_dir():
        print(f"Hata: Dizin bulunamadı: {path}", file=sys.stderr)
        sys.exit(1)

    print(f"Indexleniyor: {path}")
    rag = LlamaChromaRAG()
    count = rag.index_directory(str(path))
    print(f"Tamamlandı. Indexlenen chunk sayısı: {count}")


if __name__ == "__main__":
    main()
