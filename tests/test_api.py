import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ["CHATBOT_API_TOKEN"] = "test-token"
from app.rag_api import app

client = TestClient(app, raise_server_exceptions=False)


def test_chat_auth_failure():
    response = client.post("/chat", json={"question": "hi"})
    assert response.status_code == 401


def test_chat_success(monkeypatch):
    class Dummy:
        def encode(self, x):
            return [[0.0]]

    class Col:
        def query(self, query_embeddings, n_results):
            return {"documents": [["doc"]]}

    monkeypatch.setattr("app.rag_api._embedder", Dummy())
    monkeypatch.setattr("app.rag_api._collection", Col())
    headers = {"X-API-Token": "test-token"}
    response = client.post("/chat", json={"question": "hi"}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
