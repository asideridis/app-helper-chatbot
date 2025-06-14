"""FastAPI app exposing a simple RAG chatbot endpoint."""

from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware

API_TOKEN = os.getenv("CHATBOT_API_TOKEN", "secret-token")

app = FastAPI(title="App Helper Chatbot")


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware enforcing a static API token for the `/chat` endpoint."""

    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/chat":
            token = request.headers.get("X-API-Token")
            if token != API_TOKEN:
                raise HTTPException(
                    status_code=401, detail="Invalid or missing API token"
                )
        return await call_next(request)


app.add_middleware(AuthMiddleware)


class Question(BaseModel):
    question: str


@app.post("/chat")
async def chat(question: Question) -> dict[str, list[str] | str]:
    """Dummy chat endpoint returning a placeholder response in Greek."""
    return {
        "answer": "Δεν βρέθηκε σχετική πληροφορία",
        "sources": [],
    }
