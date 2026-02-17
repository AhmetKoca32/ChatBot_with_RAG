# ChatBot with RAG

Python tabanlı, FastAPI kullanan **RAG chatbot** projesi. LlamaIndex ile RAG eklenecek; agent/LangGraph yok. Clean Architecture prensiplerine uygun.

## Proje Yapısı

- **domain/** – Entity'ler, modeller (AI’dan bağımsız)
- **application/** – Use-case’ler ve port (interface) tanımları
- **infrastructure/** – LLM, Vector DB (LlamaIndex), PDF/doküman (ileride)
- **interfaces/** – FastAPI rotaları, Pydantic Request/Response şemaları

Bağımlılık yönetimi için Dependency Injection (FastAPI `Depends`) kullanılır.

## Kurulum

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -e .
```

## Çalıştırma

```bash
uvicorn main:app --reload
```

- **Health:** `GET http://localhost:8000/health`
- **Chat:** `POST http://localhost:8000/chat/`  
  Body: `{"message": "Merhaba"}` → RAG ile zenginleştirilmiş yanıt ve `sources` döner.

## Doküman indexleme

RAG index’ini güncellemek için (proje kökünden):

```bash
python scripts/index_docs.py
```

Varsayılan dizin: `data/documents`. Farklı bir dizin için:

```bash
python scripts/index_docs.py path/to/dosyalar
```

## Sonraki Adım

LlamaIndex eklenerek spor salonu PDF’leri indexlenip RAG sorguları bu yapı üzerinden verilecek.
