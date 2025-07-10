"""FastAPI app exposing a RAG chatbot."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from llama_cpp import Llama
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings
from .retriever import add_documents, retrieve

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")

SYSTEM_PROMPT = (
    "Είσαι ένας έμπειρος βοηθός. "
    "Απάντησε στα Ελληνικά όταν η ερώτηση είναι στα Ελληνικά, αλλιώς στα Αγγλικά.\n"
    "Χρησιμοποίησε παραπομπές όπου χρειάζεται. Αγγλικοί τεχνικοί όροι επιτρέπονται."
)


class CircuitBreaker:
    def __init__(self, fail_max: int, reset_timeout: float) -> None:
        self.fail_max = fail_max
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.open_until = 0.0

    def call(self, func, *args, **kwargs):
        if time.monotonic() < self.open_until:
            raise RuntimeError("circuit_open")
        try:
            result = func(*args, **kwargs)
            self.failures = 0
            return result
        except Exception:
            self.failures += 1
            if self.failures >= self.fail_max:
                self.open_until = time.monotonic() + self.reset_timeout
            raise


breaker = CircuitBreaker(2, 30)
try:
    model = Llama(model_path=settings.model_name)
except Exception as exc:  # pragma: no cover - heavy model load may fail
    logging.warning("Model unavailable: %s", exc)
    model = None

app = FastAPI(title="App Helper Chatbot")


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/chat") or request.url.path.startswith(
            "/ingest"
        ):
            token = request.headers.get("X-API-Token")
            if token != settings.api_token:
                return JSONResponse(status_code=401, content={"detail": "unauthorized"})
        return await call_next(request)


app.add_middleware(AuthMiddleware)


class Question(BaseModel):
    question: str


class IngestItem(BaseModel):
    text: str
    source: str


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    try:
        await asyncio.wait_for(asyncio.to_thread(breaker.call, model, "ping"), 2)
        return {"status": "ok"}
    except Exception:
        raise HTTPException(status_code=503, detail={"error": "llm_down"})


@app.post("/ingest/{app_id}")
async def ingest(app_id: str, item: IngestItem) -> dict[str, int]:
    docs = [(item.text, {"source": item.source})]
    try:
        add_documents(app_id, docs)
        return {"loaded": 1}
    except Exception as exc:  # pragma: no cover - ingestion errors
        logging.error("Ingestion failed: %s", exc)
        raise HTTPException(500, "internal_error")


async def call_model(prompt: str) -> str:
    if model is None:
        raise RuntimeError("model_unavailable")
    output = await asyncio.to_thread(breaker.call, model, prompt, max_tokens=512)
    if isinstance(output, dict):
        text = output["choices"][0]["text"]
    else:
        text = str(output)
    return text.strip()


@app.post("/chat/{app_id}")
async def chat(app_id: str, question: Question) -> dict[str, Any]:
    if time.monotonic() < breaker.open_until:
        raise HTTPException(status_code=503, detail={"error": "llm_down"})
    try:
        docs, metas = retrieve(app_id, question.question)
        context = "\n".join(docs)
        prompt = f"{SYSTEM_PROMPT}\n\ncontext:\n{context}\n\nΕρώτηση: {question.question}\nΑπάντηση:"
        answer = await call_model(prompt)
        citations = [m.get("source", "") for m in metas]
        return {"answer": answer, "citations": citations}
    except RuntimeError as exc:
        if str(exc) == "circuit_open":
            raise HTTPException(status_code=503, detail={"error": "llm_down"})
        raise
    except Exception as exc:  # pragma: no cover - unexpected errors
        logging.error("Chat failed: %s", exc)
        raise HTTPException(500, "internal_error")
