import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import types

from app import retriever


class DummyCollection:
    def __init__(self):
        self.docs: list[str] = []
        self.metas: list[dict] = []

    def add(self, documents, embeddings=None, metadatas=None):
        self.docs.extend(documents)
        self.metas.extend(metadatas or [{}])

    def query(self, query_embeddings, n_results):
        return {
            "documents": [self.docs[:n_results]],
            "metadatas": [self.metas[:n_results]],
        }


class DummyClient:
    def __init__(self, col):
        self.col = col

    def get_or_create_collection(self, name):
        return self.col


class DummyEmbedder:
    def __init__(self):
        self.last: str | None = None

    def encode(self, texts):
        self.last = texts[0]
        return [[0.0]]


def test_accent_insensitive_retrieval(monkeypatch):
    col = DummyCollection()
    client = DummyClient(col)
    embed = DummyEmbedder()
    monkeypatch.setattr(retriever, "_client", client)
    monkeypatch.setattr(retriever, "_embedder", embed)

    retriever.add_documents("test", [("Το ERP σύστημα", {"source": "s#1"})])
    docs, _ = retriever.retrieve("test", "ERP;")

    assert embed.last == "erp;"
    assert docs[0] == "Το ERP σύστημα"
