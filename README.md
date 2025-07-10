# App Helper Chatbot

A retrieval-augmented generation (RAG) service that answers **only in Greek**.  
It stores documentation per application (separate Chroma collections) and lets users ask questions through a simple FastAPI endpoint.

## Tech stack

| Purpose              | Component                    |
|----------------------|------------------------------|
| Web API              | FastAPI                      |
| Vector store         | ChromaDB                     |
| Local LLM backend    | `llama-cpp-python` via Ollama |
| Embeddings           | SentenceTransformers         |
| Container workflow   | Docker Compose               |

## Clone & install

```bash
git clone https://github.com/asideridis/app-helper-chatbot.git
cd app-helper-chatbot
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then edit as needed
```

## Running with Docker Compose (dev)

```bash
make compose-up   # starts Chroma, Ollama, and the API
make dev          # FastAPI with autoreload on http://localhost:8080
```

---

## Ingesting documents

Split a PDF into chunks and load it for a specific application:

```bash
python scripts/ingest.py   --app-id my_app   --path docs/manual.pdf   --chunk-size 400   --overlap 50
```

Each `app_id` gets its own Chroma collection (`app_my_app`, `app_hr`, etc.).

## Querying the API

```bash
curl -X POST http://localhost:8080/chat/my_app   -H "Content-Type: application/json"   -H "X-API-Token: secret-token"   -d '{"question": "Τί είναι ERP;"}'
```

Response:

```json
{
  "answer": "…",
  "citations": [
    {
      "page": 12,
      "file": "manual.pdf"
    }
  ]
}
```

---

## Deploying with systemd (optional)

```ini
# /etc/systemd/system/app-helper.service
[Unit]
Description=App Helper Chatbot API
After=network.target

[Service]
WorkingDirectory=/opt/app-helper-chatbot
ExecStart=/usr/local/bin/uvicorn app.rag_api:app --host 0.0.0.0 --port 8080
Restart=always
EnvironmentFile=/opt/app-helper-chatbot/.env

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now app-helper.service
```

---

## Environment variables

| Variable            | Purpose                                   |
|---------------------|-------------------------------------------|
| `MODEL_NAME`        | Path or tag of the GGUF model             |
| `CHROMA_HOST`       | ChromaDB host (default: `localhost`)      |
| `CHROMA_PORT`       | ChromaDB port (default: `8000`)           |
| `EMBEDDING_MODEL`   | SentenceTransformer model name            |
| `CHATBOT_API_TOKEN` | Static API token expected by the server   |

---

## Tests

```bash
make test
```

---

## License

MIT
