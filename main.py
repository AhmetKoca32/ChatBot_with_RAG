"""
Entry point: FastAPI app with Dependency Injection and Hello Agent flow.
Run: uvicorn main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.interfaces.api import agent_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown hooks (e.g. connect to Vector DB later)."""
    yield
    # teardown if needed


app = FastAPI(
    title="ChatBot with RAG",
    description="Agentic RAG API with LangGraph and Clean Architecture",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(agent_router)


@app.get("/health")
def health() -> dict:
    """Health check."""
    return {"status": "ok"}
