# ChatBot with RAG

Python tabanlı, FastAPI ve LangGraph kullanan **Agentic RAG** projesi. Clean Architecture prensiplerine uygun yapıdadır.

## Proje Yapısı

- **domain/** – Entity'ler, modeller ve AI’dan bağımsız iş mantığı
- **application/** – Use-case’ler, LangGraph akışları ve port (interface) tanımları
- **infrastructure/** – Vector DB, LLM servisleri, Tool’lar (Search, PDF parser vb.)
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
- **Hello Agent:** `POST http://localhost:8000/agent/hello`  
  Body: `{"message": "Ahmet"}` → Agent selamlama döner.

## Kullanım

- `POST /agent/hello`: Örnek “Hello Agent” akışı (LangGraph). İsteğe bağlı `message` ile isim gönderilir; yanıt Pydantic ile validate edilir.
