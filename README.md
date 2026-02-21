# ChatBot with RAG

Python tabanlı, FastAPI kullanan **RAG chatbot** projesi. LlamaIndex ile RAG eklenecek; agent/LangGraph yok. Clean Architecture prensiplerine uygun.

## Proje Yapısı

- **domain/** – Entity'ler, modeller (AI’dan bağımsız)
- **application/** – Use-case’ler ve port (interface) tanımları
- **infrastructure/** – LLM, Vector DB (LlamaIndex), PDF/doküman (ileride)
- **interfaces/** – FastAPI rotaları, Pydantic Request/Response şemaları
- **streamlit_app.py** – Chat arayüzü (frontend); backend'e HTTP ile bağlanır

Bağımlılık yönetimi için Dependency Injection (FastAPI `Depends`) kullanılır.

## Kurulum

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -e .
```

## Çalıştırma

**1. Backend (FastAPI)** — bir terminalde:

```bash
uvicorn main:app --reload
```

- **Health:** `GET http://localhost:8000/health`
- **Chat API:** `POST http://localhost:8000/chat/`  
  Body: `{"message": "Merhaba"}` → RAG ile zenginleştirilmiş yanıt ve `sources` döner.

**2. Frontend (Streamlit)** — ikinci bir terminalde:

```bash
streamlit run streamlit_app.py
```

Tarayıcıda açılan sayfadan mesaj yazıp RAG cevabı ve kaynakları görebilirsin. Backend'in `http://localhost:8000` adresinde çalışıyor olması gerekir.

## Doküman indexleme

RAG index’ini güncellemek için (proje kökünden):

```bash
python scripts/index_docs.py
```

Varsayılan dizin: `data/documents`. Farklı bir dizin için:

```bash
python scripts/index_docs.py path/to/dosyalar
```

## Deploy (Streamlit Cloud)

Sadece **arayüzü** deploy etmek için (backend ayrı bir yerde çalışacak):

1. Repoyu GitHub'a pushlayın.
2. [share.streamlit.io](https://share.streamlit.io) → "New app" → repo ve `streamlit_app.py` seçin.
3. **Advanced settings** → Environment variables:
   - `CHAT_API_URL`: Backend'in adresi (örn. `https://your-fastapi.railway.app` veya Render/Fly.io URL).
4. Paket kurulumu: `pip install -e .` veya `pip install -r requirements.txt`.

Streamlit Cloud sadece arayüzü çalıştırır; **backend'i ayrıca** bir serviste (Railway, Render, Fly.io, vb.) deploy etmeniz gerekir. Backend'de `DEEPSEEK_API_KEY`, `CHROMA_PERSIST_DIR` (ve Chroma verisi) ayarlanmalıdır.

## Sonraki Adım

LlamaIndex eklenerek spor salonu PDF’leri indexlenip RAG sorguları bu yapı üzerinden verilecek.
