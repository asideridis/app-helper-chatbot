"""FastAPI app exposing a simple RAG chatbot endpoint."""

from __future__ import annotations

import logging
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import chromadb
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware
import time

API_TOKEN = os.getenv("CHATBOT_API_TOKEN", "secret-token")

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")

DB_DIR = os.getenv("CHROMA_DB", os.path.expanduser("~/chatbot/chroma"))

_client = chromadb.PersistentClient(path=DB_DIR)
_collection = _client.get_or_create_collection("app-helper")

try:
    from sentence_transformers import SentenceTransformer

    _embedder = SentenceTransformer("intfloat/multilingual-e5-large")
except Exception as exc:  # pragma: no cover - heavy import may fail in tests
    logging.warning("SentenceTransformer unavailable: %s", exc)
    _embedder = None

app = FastAPI(title="App Helper Chatbot")


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware enforcing a static API token for the `/chat` endpoint."""

    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/chat":
            token = request.headers.get("X-API-Token")
            if token != API_TOKEN:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid or missing API token"},
                )
        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter per client IP."""

    def __init__(self, app: FastAPI, limit: int = 60, window: int = 60) -> None:
        super().__init__(app)
        self.limit = limit
        self.window = window
        self.clients: dict[str, tuple[int, int]] = {}

    async def dispatch(self, request: Request, call_next):
        ip = request.client.host if request.client else "anonymous"
        now = int(time.time())
        count, last = self.clients.get(ip, (0, now))
        if now - last >= self.window:
            count = 0
            last = now
        if count >= self.limit:
            raise HTTPException(429, "Rate limit exceeded")
        self.clients[ip] = (count + 1, last)
        return await call_next(request)


app.add_middleware(AuthMiddleware)
app.add_middleware(RateLimitMiddleware)


class Question(BaseModel):
    question: str


@app.post("/chat")
async def chat(question: Question) -> dict[str, list[str] | str]:
    """Retrieve relevant chunks and return them as the answer."""
    query = question.question
    try:
        if _embedder is None:
            raise RuntimeError("Embedder not available")
        q_emb = _embedder.encode([query])[0]
        results = _collection.query(query_embeddings=[q_emb], n_results=3)
        docs = results.get("documents", [[]])[0]
        if not docs:
            return {"answer": "Δεν βρέθηκε σχετική πληροφορία", "sources": []}
        answer = "\n".join(docs)
        return {"answer": answer, "sources": []}
    except Exception as exc:  # pragma: no cover - retrieval errors
        logging.error("Chat failed: %s", exc)
        raise HTTPException(500, "Internal error")
