# Mimari Detayları — ChatBot with RAG

Bu dokümanda projenin **Clean Architecture** yapısı, her katmandaki bileşenler ve veri akışı detaylıca anlatılmaktadır.

---

## 1. Genel Bakış

Mimari dört ana katmandan oluşur. Bağımlılık yönü **içe doğru**: dış katmanlar iç katmanlara bağımlıdır, domain hiçbir dış katmana bağımlı değildir.

```
                    ┌─────────────────────────────────────────┐
                    │              interfaces/                 │  ← HTTP, şemalar
                    │   (FastAPI rotaları, Request/Response)   │
                    └────────────────────┬────────────────────┘
                                          │
                    ┌────────────────────▼────────────────────┐
                    │            application/                  │  ← Use-case, graflar
                    │  (Use-case'ler, LangGraph akışları,     │
                    │   port'lar / interface'ler)               │
                    └────────────────────┬────────────────────┘
                                          │
        ┌─────────────────────────────────┼─────────────────────────────────┐
        │                                 │                                 │
        ▼                                 ▼                                 ▼
┌───────────────┐               ┌───────────────────┐               ┌───────────────┐
│   domain/     │               │  infrastructure/  │               │   domain/     │
│ (entity,      │               │ (LLM, Vector DB,  │               │ (tekrar)      │
│  model)       │               │  Tool'lar)        │               │               │
└───────────────┘               └───────────────────┘               └───────────────┘
```

- **domain**: Hiçbir framework veya dış servise bağımlı değil; sadece Python stdlib + Pydantic/dataclass.
- **application**: Sadece `domain` ve kendi **port**'larına (soyut interface) bağımlı. LangGraph grafları burada.
- **infrastructure**: **Port**'ları somutlaştırır (LLM, DB, araçlar). Application’ın beklediği interface’leri implement eder.
- **interfaces**: HTTP dünyası; FastAPI, Pydantic şemaları ve **Dependency Injection** bağlamı. Application use-case’lerini çağırır.

---

## 2. Katmanlar ve İçerikleri

### 2.1 Domain (`src/domain/`)

**Amaç:** İş mantığının ve veri yapılarının AI/framework’ten bağımsız tanımı.

| Dosya | İçerik | Açıklama |
|-------|--------|----------|
| `entities.py` | `Role`, `Message`, `ConversationTurn` | Saf iş nesneleri. `Message` değişmez (frozen), `Role` enum. LLM veya API’den bahsetmez. |
| `models.py` | `AgentState` | Pydantic model; agent state’i için alanlar ve validasyon. İsteğe bağlı ek alanlara `extra="allow"` ile izin verilir (LangGraph uyumu). |

**Bağımlılık:** Sadece `dataclasses`, `datetime`, `enum`, `pydantic`. Hiçbir `application`, `infrastructure` veya `interfaces` import’u yok.

---

### 2.2 Application (`src/application/`)

**Amaç:** Kullanıcı/istemci isteğini “ne yapılacak” (use-case) ve “nasıl akacağı” (LangGraph) olarak tanımlamak. Dış dünya ile iletişim **sadece port’lar (interface)** üzerinden.

#### 2.2.1 Port’lar — `application/interfaces/`

| Dosya | İçerik | Açıklama |
|-------|--------|----------|
| `llm_gateway.py` | `LLMGateway` (ABC) | Soyut LLM arayüzü. Tek metot: `invoke(prompt: str, **kwargs) -> str`. Application katmanı sadece bu interface’e bağımlı; gerçek LLM’in OpenAI mi, fake mi olduğunu bilmez. |

Application, `LLMGateway`’i **kullanır**; implementasyonu **infrastructure** sağlar (ör. `FakeLLMGateway`, ileride `OpenAIGateway`).

#### 2.2.2 Akışlar (LangGraph) — `application/flows/`

| Dosya | İçerik | Açıklama |
|-------|--------|----------|
| `hello_agent.py` | `HelloAgentState`, `create_hello_agent_graph(llm_gateway)` | **Hello Agent** grafı. State: `messages`, `current_input`, `response`. Tek node: kullanıcı girişini alır, `llm_gateway.invoke(...)` ile cevap üretir, state’i günceller. Graf `START → process → END`. |

- Graf **application**’da tanımlanır; LLM çağrısı **port** üzerinden yapılır.
- State LangGraph için `TypedDict`; mesaj birleştirme `add_messages` ile.

#### 2.2.3 Use-Case’ler — `application/use_cases/`

| Dosya | İçerik | Açıklama |
|-------|--------|----------|
| `hello_agent.py` | `HelloAgentUseCase` | Constructor’da `LLMGateway` alır (DI). `run(user_input: str) -> str`: başlangıç state’ini oluşturur, `create_hello_agent_graph(...).invoke(initial_state)` çağırır, dönen state’ten `response`’u döner. |

Use-case, “Hello Agent’ı çalıştır” işini tek bir giriş noktasıyla ifade eder; HTTP veya CLI fark etmez.

**Application’ın bağımlılıkları:** `domain` (gerekirse), kendi `interfaces` (port) ve LangGraph. **infrastructure** veya **interfaces** (FastAPI) import edilmez.

---

### 2.3 Infrastructure (`src/infrastructure/`)

**Amaç:** Port’ların gerçek implementasyonları (LLM, veritabanı, araçlar).

| Bölüm | Dosya / Klasör | İçerik | Açıklama |
|-------|----------------|--------|----------|
| LLM | `llm/fake_llm_gateway.py` | `FakeLLMGateway` | `LLMGateway`’i implement eder. API key gerektirmez; prompt’tan isim çıkarıp “Hello, {isim}!” döner. Gerçek LLM için burada `ChatOpenAI` vb. kullanılacak yeni bir sınıf eklenir. |
| LLM | `llm/__init__.py` | — | LLM modülü export’ları. |
| Araçlar | `tools/` | (placeholder) | İleride Search, PDF parser vb. tool’lar burada tanımlanacak. |
| Vector DB | `vector_db/` | (placeholder) | RAG için vektör veritabanı (Chroma, Qdrant vb.) burada bağlanacak. |

**Bağımlılık:** `application.interfaces` (port’ları implement etmek için). Domain’e doğrudan bağımlılık olabilir (entity/model kullanımı), ama application’ın iş akışına müdahale etmez.

---

### 2.4 Interfaces (`src/interfaces/`)

**Amaç:** Dış dünya (HTTP) ile uygulamanın buluştuğu yer: rotalar, şemalar ve **Dependency Injection** tanımları.

| Bölüm | Dosya | İçerik | Açıklama |
|-------|--------|--------|----------|
| Şemalar | `schemas/agent.py` | `HelloAgentRequest`, `HelloAgentResponse` | Pydantic ile gelen istek ve giden yanıtın validasyonu. Örn. `message` uzunluk sınırı, `response` ve `success` alanları. |
| API | `api/agent.py` | `router`, `hello_agent` endpoint | `POST /agent/hello`. Body → `HelloAgentRequest`; use-case `Depends(get_hello_agent_use_case)` ile alınır; `use_case.run(body.message)` çağrılır; sonuç `HelloAgentResponse` ile döner. |
| DI | `dependencies.py` | `get_llm_gateway`, `get_hello_agent_use_case` | `get_llm_gateway()` somut LLM’i döner (şu an `FakeLLMGateway`). `get_hello_agent_use_case(llm_gateway=Depends(get_llm_gateway))` use-case’i gateway ile oluşturur. Böylece tek bir yerde (veya env’e göre) LLM değiştirilebilir. |

**Bağımlılık:** FastAPI, `application.use_cases`, `application.interfaces`, `infrastructure.llm` (sadece DI fonksiyonlarında). Rota sadece use-case’i çağırır; LLM veya graf detayı bilmez.

---

## 3. Bir İstek Nasıl İşlenir?

Örnek: `POST /agent/hello` ile `{"message": "Ahmet"}` gönderilir.

1. **interfaces**  
   - FastAPI body’yi `HelloAgentRequest` ile parse eder (Pydantic validasyon).  
   - `get_hello_agent_use_case` çağrılır → `get_llm_gateway()` ile `FakeLLMGateway` alınır → `HelloAgentUseCase(llm_gateway=...)` oluşturulur.  
   - Rota: `use_case.run(body.message)` → `"Ahmet"` geçer.

2. **application (use-case)**  
   - `HelloAgentUseCase.run("Ahmet")`:  
     - `initial_state = { "messages": [], "current_input": "Ahmet", "response": "" }`.  
     - `self._graph.invoke(initial_state)` çağrılır.

3. **application (flow)**  
   - LangGraph `process` node’u çalışır.  
   - `state["current_input"]` → `"Ahmet"`.  
   - `llm_gateway.invoke("Generate a short friendly greeting for the name: Ahmet. ...")` çağrılır.

4. **infrastructure**  
   - `FakeLLMGateway.invoke(...)` prompt’tan ismi çıkarır, `"Hello, Ahmet!"` döner.

5. **application (flow)**  
   - Node state’i günceller: `{"response": "Hello, Ahmet!", "messages": [...]}`.  
   - Graf biter, bu state use-case’e döner.

6. **application (use-case)**  
   - `result.get("response", "")` → `"Hello, Ahmet!"` döner.

7. **interfaces**  
   - Rota `HelloAgentResponse(response="Hello, Ahmet!", success=True)` döner; FastAPI JSON’a çevirir.

Özet akış: **HTTP → Şema → DI → Use-case → LangGraph → Port (LLMGateway) → Infrastructure → Cevap aynı zincirle geri döner.**

---

## 4. Bağımlılık Yönleri (Özet)

- **domain:** Dışarıya bağımlılık yok (sadece stdlib + pydantic/dataclass).
- **application:** Sadece `domain` + kendi **port**’larına (örn. `LLMGateway`) bağımlı. Infrastructure’ı tanımaz.
- **infrastructure:** Port’ları implement eder; `application.interfaces` ve gerekirse `domain` kullanır.
- **interfaces:** Use-case’leri ve DI ile somut implementasyonları (infrastructure) bir araya getirir; HTTP ve şemalar burada.

Bu sayede testte `LLMGateway` mock’lanabilir, production’da farklı bir LLM veya Vector DB eklenebilir; use-case ve graf kodu değişmeden kalır.

---

## 5. Klasör Özeti (Referans)

```
src/
├── domain/                    # Entity, model; AI/framework bağımsız
│   ├── entities.py            # Message, ConversationTurn, Role
│   └── models.py              # AgentState (Pydantic)
├── application/
│   ├── interfaces/            # Port’lar (soyut)
│   │   └── llm_gateway.py     # LLMGateway
│   ├── flows/                 # LangGraph grafları
│   │   └── hello_agent.py     # Hello Agent StateGraph
│   └── use_cases/             # Use-case sınıfları
│       └── hello_agent.py     # HelloAgentUseCase
├── infrastructure/            # Port implementasyonları
│   ├── llm/
│   │   └── fake_llm_gateway.py  # FakeLLMGateway
│   ├── tools/                   # (Search, PDF vb. — placeholder)
│   └── vector_db/               # (RAG — placeholder)
└── interfaces/                # HTTP, şemalar, DI
    ├── dependencies.py       # get_llm_gateway, get_hello_agent_use_case
    ├── schemas/
    │   └── agent.py           # HelloAgentRequest, HelloAgentResponse
    └── api/
        └── agent.py          # POST /agent/hello
```

Bu yapı, RAG ve yeni agent akışları eklendiğinde de aynı katman disipliniyle büyümek için tasarlanmıştır.
