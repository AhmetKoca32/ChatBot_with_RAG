"""
Streamlit frontend for RAG ChatBot.
Connects to FastAPI backend (POST /chat/). Set CHAT_API_URL for deployment.
Run: streamlit run streamlit_app.py
"""

import os
import sys
from pathlib import Path

# Project root
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import httpx
import streamlit as st

# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------
API_BASE = os.getenv("CHAT_API_URL", "http://localhost:8000")
CHAT_URL = f"{API_BASE.rstrip('/')}/chat/"
HEALTH_URL = f"{API_BASE.rstrip('/')}/health"
REQUEST_TIMEOUT = 60.0


def _escape_html(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


# -----------------------------------------------------------------------------
# Page config & custom CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="RAG ChatBot",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    /* Header */
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.25rem;
    }
    .main-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-bottom: 2rem;
    }
    /* Chat container */
    .stChatMessage {
        border-radius: 1rem;
        padding: 1rem 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }
    /* Source pills */
    .source-pill {
        display: inline-block;
        background: rgba(99, 102, 241, 0.2);
        color: #a5b4fc;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        margin: 0.2rem 0.2rem 0.2rem 0;
    }
    /* Status badge */
    .status-ok { color: #34d399; }
    .status-err { color: #f87171; }
    /* Input area */
    .block-container { padding-top: 1.5rem; max-width: 900px; margin: 0 auto; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Session state
# -----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_checked" not in st.session_state:
    st.session_state.api_checked = None  # True/False/None

# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Ayarlar")
    api_url = st.text_input(
        "Backend API URL",
        value=API_BASE,
        help="FastAPI backend adresi (deploy'da CHAT_API_URL kullanın)",
    )
    chat_endpoint = f"{api_url.rstrip('/')}/chat/"
    health_endpoint = f"{api_url.rstrip('/')}/health"

    if st.button("🔌 Bağlantıyı kontrol et"):
        try:
            r = httpx.get(health_endpoint, timeout=5.0)
            st.session_state.api_checked = r.status_code == 200
        except Exception:
            st.session_state.api_checked = False
        st.rerun()

    if st.session_state.api_checked is True:
        st.success("Backend bağlı")
    elif st.session_state.api_checked is False:
        st.error("Backend ulaşılamıyor. Backend'i çalıştırın: `uvicorn main:app --reload`")

    st.markdown("---")
    st.markdown("""
    **Nasıl kullanılır**
    - Aşağıya sorunuzu yazıp Enter veya Gönder'e tıklayın.
    - Cevap RAG (dokümanlar) + LLM ile oluşturulur.
    - Kaynaklar cevabın altında listelenir.
    """)
    if st.button("🗑️ Sohbeti temizle"):
        st.session_state.messages = []
        st.rerun()

# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
st.markdown('<p class="main-header">RAG ChatBot</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="main-subtitle">Dokümanlarınıza dayalı soru-cevap. Spor salonu bilgileri, kurallar, fiyatlar ve daha fazlası.</p>',
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Chat history
# -----------------------------------------------------------------------------
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    sources = msg.get("sources") or []

    with st.chat_message(role):
        st.markdown(content)
        if role == "assistant" and sources:
            st.markdown("**Kaynaklar:**")
            labels = [Path(s).name if len(s) > 40 else s for s in sources]
            pills = " ".join([f'<span class="source-pill">{_escape_html(lb)}</span>' for lb in labels])
            st.markdown(pills, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Chat input & send
# -----------------------------------------------------------------------------
if prompt := st.chat_input("Mesajınızı yazın..."):
    # Append user message
    st.session_state.messages.append({"role": "user", "content": prompt, "sources": []})

    # Show user message immediately
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call API and show assistant reply
    with st.chat_message("assistant"):
        with st.spinner("Cevap hazırlanıyor..."):
            try:
                with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
                    r = client.post(chat_endpoint, json={"message": prompt})
                r.raise_for_status()
                data = r.json()
                response_text = data.get("response", "")
                sources = data.get("sources", [])
            except httpx.ConnectError:
                response_text = "Backend'e bağlanılamadı. Lütfen FastAPI'yi çalıştırın: `uvicorn main:app --reload`"
                sources = []
            except httpx.HTTPStatusError as e:
                response_text = f"API hatası ({e.response.status_code}). Lütfen backend loglarına bakın."
                sources = []
            except Exception as e:
                response_text = f"Hata: {e!s}"
                sources = []

            st.markdown(response_text)
            if sources:
                st.markdown("**Kaynaklar:**")
                for s in sources:
                    # Show only filename if path is long
                    label = Path(s).name if len(s) > 40 else s
                    st.markdown(f'<span class="source-pill">{_escape_html(label)}</span>', unsafe_allow_html=True)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text,
        "sources": sources,
    })
    st.rerun()
