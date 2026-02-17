# ChatBot with RAG – Geliştirme ve Sorun Giderme Özeti

Bu doküman, projenin RAG chatbot aşamasında yapılan değişiklikleri, karşılaşılan hataları ve çözümleri kronolojik ve konu bazlı olarak özetler.

---

## 1. Başlangıç Durumu

- **Mimari:** Clean Architecture (domain, application, infrastructure, interfaces) kuruluydu.
- **RAG:** LlamaIndex + Chroma + HuggingFace embedding ile `LlamaChromaRAG` vardı; `index_directory` ve `retrieve` çalışıyordu.
- **Eksik:** Chat akışı sadece LLM kullanıyordu; RAG context’e bağlı değildi.

---

## 2. Yapılan Değişiklikler ve Karşılaşılan Sorunlar

### 2.1 RAG’ı Chat’e Bağlama

**Yapılanlar:**
- `ChatUseCase` içine `RAGGateway` enjekte edildi.
- `run()`: kullanıcı mesajı için `retrieve(query, top_k)` → gelen chunk’lar context olarak LLM prompt’una eklendi; cevap + `sources` döndürüldü.
- `dependencies.py`: `get_rag_gateway()` (LlamaChromaRAG) eklendi; `get_chat_use_case` RAG’a bağlandı.
- Chat API: use case’ten gelen `result.response` ve `result.sources` response schema’ya verildi.

**Sonuç:** Chat artık RAG ile cevap veriyordu; ancak index boş olduğunda `sources: []` ve “bağlamda bilgi yok” cevabı geliyordu (beklenen davranış).

---

### 2.2 Doküman Indexleme Script’i

**Yapılanlar:**
- `scripts/index_docs.py` eklendi: `LlamaChromaRAG().index_directory(path)` çağrılıyor; varsayılan path `data/documents`.
- README’ye “Doküman indexleme” bölümü eklendi.

**Kullanım:** PDF/txt’leri `data/documents`’a koyup `python scripts/index_docs.py` çalıştırıldığında index güncellenir.

---

### 2.3 DeepSeek LLM Entegrasyonu

**Yapılanlar:**
- `src/infrastructure/llm/deepseek_llm_gateway.py`: OpenAI uyumlu client, `base_url="https://api.deepseek.com"`, model `deepseek-chat`.
- `dependencies.py`: `DEEPSEEK_API_KEY` env’de varsa `DeepSeekLLMGateway`, yoksa `FakeLLMGateway` kullanılıyor.
- `main.py`: Uygulama başında `load_dotenv()` çağrılıyor.
- `.env.example`: `DEEPSEEK_API_KEY` ve isteğe bağlı değişkenler dokümante edildi.

**Hata 1 – `ModuleNotFoundError: No module named 'openai'`**  
- **Sebep:** Proje bağımlılıkları (venv) yüklenmemişti veya uvicorn venv dışındaki Python ile çalışıyordu.
- **Çözüm:** venv aktif edildi (`.\.venv\Scripts\Activate.ps1`), `pip install -e .` çalıştırıldı.

---

### 2.4 Fiyat / Üyelik Sorularında Cevap Gelmemesi

**Belirti:** “Aylık ücret ne?” gibi sorularda `sources` dolu (PDF 2 listeleniyor) ama cevap “bağlamda bilgi yok” diyordu.

**Sebep:** Semantic search bazen dokümanın **başındaki** fiyat listesi chunk’ını getirmiyordu; daha çok “Ödeme Koşulları”, “İptal” gibi bölümler geliyordu.

**Denenen çözümler (sonradan kaldırıldı):**
- `top_k` artırıldı; ek “anahtar kelime” sorgusu (üyelik, fiyat, TL) ile ikinci bir `retrieve` ve birleştirme.
- Tag tabanlı çözüm: `tag_uyelik` metadata ile “Üyelik” içeren dosyanın ilk N chunk’ını `get_first_chunks("üyelik")` ile zorla ekleme.

Bu yaklaşımlar soru tipi başına özel kod gerektirdiği için sürdürülebilir bulunmadı; yerine **genel “doc_start”** kuralına geçildi (aşağıda).

---

### 2.5 Genel Kural: Her Dokümanın Başından Chunk (doc_start)

**Yapılanlar:**
- Index sırasında her node’a `chunk_index` (dosya içi sıra) ve `doc_start = "1"` (ilk N chunk) metadata’sı eklendi.
- `RAGGateway`’e `get_doc_start_chunks()` eklendi; Chroma’da `doc_start == "1"` olan chunk’ları döndürüyor.
- Chat use case: **her soruda** `retrieve(query)` + `get_doc_start_chunks()` birleştirilip context oluşturuldu. Böylece kurallar, fiyat, program, saat bilgisi tek mantıkla (doküman başı) gelmeye başladı.
- LlamaIndex metadata’da sadece str/int/float kabul ettiği için `doc_start` string `"1"` / `"0"` olarak tutuldu; liste (tags) kullanılamadı.

**Sonuç:** Soru tipine özel kod kalktı; tek kural ile tüm “rehber” içerikleri context’e alındı.

---

### 2.6 Salon Saatleri / Kurallar Sorularında Hâlâ Cevap Yok

**Belirti:** “Salon kaçta açılıyor?”, “Salon kullanım kuralları neler?” sorularında `sources`’ta PDF 1 / PDF 3 görünüyordu ama cevap “bağlamda bilgi yok” diyordu.

**Kök neden – Debug ile tespit:**  
`GET /chat/debug` endpoint’i eklendi; dönen `context_preview` incelendi. Context’te **gerçek metin yerine ham PDF içeriği** vardı: `%PDF-1.4`, `obj`, `stream`, XML metadata vb.

**Sebep:** `SimpleDirectoryReader` PDF dosyasını **metin olarak çıkarmıyor**, ham okuyordu. Bu yüzden chunk’lar anlamsız; “07:00”, “Pazartesi” gibi ifadeler context’te yoktu.

**Çözüm:**
- **pypdf** eklendi; index tarafında `SimpleDirectoryReader` kaldırıldı.
- `_load_documents_from_dir()`: Her PDF için `pypdf.PdfReader` ile sayfa sayfa `extract_text()` yapılıyor; çıkan metin `Document` olarak LlamaIndex’e veriliyor. `.txt` dosyaları doğrudan okunmaya devam etti.
- Index’ten itibaren tüm chunk’lar artık **gerçek metin** içeriyor.

---

### 2.7 PDF’den Gelen Metinde Harfler Arası Boşluk

**Belirti:** Debug’da `context_contains_07: true` ama `context_contains_Pazartesi: false`; `context_preview`’da “P a z a r t e s i”, “1 . 5 0 0 T L” gibi ifadeler vardı.

**Sebep:** Bazı PDF’lerde metin pozisyonu nedeniyle harf/rakam arasına boşluk yazılıyor; pypdf bunu olduğu gibi döndürüyor.

**Çözüm:** `_normalize_pdf_text()` eklendi; regex ile `(?<=[\w.]) (?=[\w.])` boşlukları kaldırılıyor. Böylece “Pazartesi”, “1.500 TL” tek parça hale geliyor; hem arama hem LLM cevabı düzeldi.

---

### 2.8 LLM’in “Bağlamda yok” Demesi (Bilgi Varken)

**Belirti:** Context’te saat/fiyat bilgisi olmasına rağmen cevap “bağlamda net bilgi yok”, “iletişime geçin” gibi ifadeler içeriyordu.

**Çözüm:** Prompt güncellendi: “Bağlamdaki saat, fiyat, kural vb. bilgiyi doğrudan kullanıp net cevap ver; cevabında bu bilgileri yazdıysan ‘bağlamda yok’ veya ‘iletişime geçin’ deme.” Böylece model, kullandığı bilgiyi inkâr etmeyi bıraktı.

---

### 2.9 Doc-Start Chunk Sayısı ve Temizlik

- **20 chunk/doc:** Başta her dokümanın ilk 20 chunk’ı doc_start sayıldı. Tüm rehber içeriği geliyordu ancak token/gürültü artışı tartışıldı.
- **12 chunk’a indirme:** Token ve gürültüyü azaltmak için 12’ye düşürüldü. Testte üyelik fiyatları ve salon kuralları tam; açılış saatlerinde kapanış/son giriş detayı bazen kısaltılabiliyor (kabul edilebilir).
- **Kullanılmayan kod temizliği:** `get_first_chunks`, `_tag_flags_from_path`, index’te tag atayan döngü ve `get_doc_start_chunks(max_chunks_per_doc)` parametresi kaldırıldı. Sadece parametresiz `get_doc_start_chunks()` kaldı.

---

### 2.10 Index Öncesi Koleksiyon Temizliği

**Sorun:** Re-index yapıldığında Chroma’ya yeni kayıtlar **ekleniyordu**; eski (tag/metadata’sız) kayıtlar kalıyordu. Karışık veya tutarsız sonuçlar oluşabiliyordu.

**Çözüm:** `index_directory()` başında mevcut koleksiyondaki tüm id’ler `get()` ile alınıp `delete(ids=...)` ile siliniyor; ardından yeni chunk’lar yazılıyor. Böylece her index işlemi temiz bir koleksiyonla başlıyor.

---

## 3. Güncel Akış Özeti

1. **Index (bir kere / güncellemede):**  
   `scripts/index_docs.py` → `_load_documents_from_dir()` (pypdf + .txt) → metin normalize → chunk (512 char, 50 overlap) → `chunk_index` + `doc_start` (ilk 12 chunk) → Chroma’ya yazma.

2. **Chat (her istek):**  
   `retrieve(query, top_k=14)` + `get_doc_start_chunks()` birleştirilir, tekrarlar (text[:80]) ile elenir → context string → LLM prompt’una “Bağlam: …” + “Kullanıcı: …” eklenir → cevap + sources döndürülür.

3. **Debug:**  
   `GET /chat/debug?q=...` ile aynı retrieval yapılıp `doc_start_count`, `context_contains_07`, `context_contains_Pazartesi`, `context_preview` döndürülür; sorun tespitinde kullanılır.

---

## 4. Clean Architecture: Vector DB Ayrımı

**Amaç:** Infrastructure içinde sorumluluk ayrımı; vector kalıcılığı ayrı adapter olsun.

**Yapılanlar:**
- **`infrastructure/vector_db/chroma_store.py`:** Chroma persistent client ve koleksiyon üretimi. `get_chroma_collection(persist_dir=..., collection_name=...)` ile tek noktadan erişim.
- **`infrastructure/rag/llama_chroma_rag.py`:** Chroma’yı doğrudan oluşturmak yerine `get_chroma_collection()` (vector_db) kullanıyor. RAG = indexing + retrieval mantığı; vector persistence = vector_db katmanı.
- **`infrastructure/vector_db/__init__.py`:** `get_chroma_collection` export edildi.
- **`infrastructure/__init__.py`:** Katman açıklaması güncellendi (llm, rag, vector_db).

**Sonuç:** Application yalnızca port’lara (RAGGateway, LLMGateway) bağımlı; Infrastructure’da RAG adapter’ı vector DB adapter’ını kullanıyor. Vector store değişirse (örn. Qdrant) sadece `vector_db` implementasyonu değişir, RAG aynı port’u kullanmaya devam eder.

---

## 5. Önemli Dosyalar

| Dosya | Rol |
|-------|-----|
| `src/application/use_cases/chat.py` | RAG + LLM akışı; retrieve + doc_start birleştirme; prompt |
| `src/infrastructure/rag/llama_chroma_rag.py` | pypdf ile yükleme, normalize, chunk, Chroma, retrieve, get_doc_start_chunks |
| `src/application/interfaces/rag_gateway.py` | RAG port: retrieve, index_directory, get_doc_start_chunks |
| `src/interfaces/api/chat.py` | POST /chat/, GET /chat/debug |
| `scripts/index_docs.py` | Dokümanları index’e alma |
| `src/infrastructure/vector_db/chroma_store.py` | Chroma client/collection (vector persistence) |

---

## 6. Sık Karşılaşılan Durumlar

- **“Bağlamda bilgi yok” ama sources dolu:** Önce `GET /chat/debug` ile context’e gerçekten metin giriyor mu kontrol edin. Giriyorsa prompt/LLM; girmiyorsa index/PDF okuma (pypdf, normalize) tarafına bakın.
- **Yeni PDF ekledim, cevap değişmedi:** Index yeniden alınmalı: `python scripts/index_docs.py`. Uygulama Chroma’yı diskten okur; index güncel olmalı.
- **venv / openai hatası:** venv aktif edip `pip install -e .` çalıştırın; uvicorn’u aynı ortamda başlatın.

Bu doküman, yapılan değişikliklerin ve çözülen hataların özetidir; ileride benzer sorunlarda referans olarak kullanılabilir.
