from __future__ import annotations

import logging
import unicodedata
from typing import Iterable, Tuple

import chromadb

try:
    from sentence_transformers import SentenceTransformer
except Exception as exc:
    logging.warning("SentenceTransformer unavailable: %s", exc)
    SentenceTransformer = None  # type: ignore

from .config import settings

_client = None
_embedder = (
    SentenceTransformer(settings.embedding_model) if SentenceTransformer else None
)


def get_client():
    global _client
    if _client is None:
        try:
            _client = chromadb.HttpClient(
                host=settings.chroma_host, port=settings.chroma_port
            )
        except Exception:
            _client = chromadb.Client()
    return _client


def normalize(text: str) -> str:
    decomp = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in decomp if unicodedata.category(ch) != "Mn").lower()


def get_collection(app_id: str):
    return get_client().get_or_create_collection(f"app_{app_id}")


def retrieve(app_id: str, query: str, k: int = 3) -> Tuple[list[str], list[dict]]:
    col = get_collection(app_id)
    emb = _embedder.encode([normalize(query)])[0]
    res = col.query(query_embeddings=[emb], n_results=k)
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    return docs, metas


def add_documents(app_id: str, docs: Iterable[Tuple[str, dict]]) -> None:
    col = get_collection(app_id)
    for text, meta in docs:
        emb = _embedder.encode([normalize(text)])[0]
        col.add(documents=[text], embeddings=[emb], metadatas=[meta])
