"""
Entry point: FastAPI app — RAG chatbot (LlamaIndex). No agent/LangGraph.
Run: uvicorn main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.interfaces.api import chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown hooks (e.g. LlamaIndex index load later)."""
    yield


app = FastAPI(
    title="ChatBot with RAG",
    description="RAG chatbot with LlamaIndex and Clean Architecture",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(chat_router)


@app.get("/health")
def health() -> dict:
    """Health check."""
    return {"status": "ok"}
