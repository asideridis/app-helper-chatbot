import asyncio
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import os

os.environ["API_TOKEN"] = "test-token"
import httpx
from httpx import ASGITransport

from app.rag_api import app

transport = ASGITransport(app=app)


def test_chat_auth_failure():
    async def run():
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            response = await client.post("/chat/app1", json={"question": "hi"})
            return response.status_code

    status = asyncio.run(run())
    assert status == 401


def test_chat_contract(monkeypatch):
    class Col:
        def query(self, query_embeddings, n_results):
            return {
                "documents": [["Η απάντηση" * 3]],
                "metadatas": [[{"source": "file#1"}]],
            }

    monkeypatch.setattr(
        "app.retriever.retrieve",
        lambda app_id, query: (["doc"], [{"source": "file#1"}]),
    )
    monkeypatch.setattr(
        "app.rag_api.retrieve", lambda app_id, query: (["doc"], [{"source": "file#1"}])
    )

    async def dummy_call(prompt: str):
        return "ok"

    monkeypatch.setattr("app.rag_api.call_model", dummy_call)
    headers = {"X-API-Token": "test-token"}

    async def run():
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            response = await client.post(
                "/chat/test_app", json={"question": "Τί είναι ERP;"}, headers=headers
            )
            return response

    response = asyncio.run(run())
    assert response.status_code == 200
    data = response.json()
    assert "citations" in data
