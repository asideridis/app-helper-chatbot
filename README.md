# App Helper Chatbot

A retrieval augmented generation (RAG) service that stores documentation per application and answers questions in Greek. The API uses FastAPI, ChromaDB and `llama-cpp-python` via Ollama.

## Tech stack

- **FastAPI** – web framework
- **ChromaDB** – vector store
- **llama-cpp-python** – local LLM backend
- **SentenceTransformers** – embeddings
- **Docker Compose** – development setup

## Clone and install

```bash
git clone https://github.com/asideridis/app-helper-chatbot.git
cd app-helper-chatbot
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Running with Docker Compose

Start Chroma, Ollama and the API:

```bash
make compose-up
make dev
```

The API listens on `http://localhost:8080`.

## Ingest documents

Split PDF files into chunks and store them by application id:

```bash
python scripts/ingest.py --app-id my_app \
  --path docs/manual.pdf --chunk-size 400 --overlap 50
```

## Query the API

```bash
curl -X POST http://localhost:8080/chat/my_app \
  -H 'Content-Type: application/json' \
  -H 'X-API-Token: secret-token' \
  -d '{"question": "Τί είναι ERP;"}'
```

The JSON response contains an `answer` and `citations` array.

## Running with systemd

Create `/etc/systemd/system/app-helper.service`:

```ini
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

Reload systemd and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now app-helper.service
```

## Environment variables

| Name              | Purpose                                  |
|-------------------|-------------------------------------------|
| `MODEL_NAME`      | Path to GGUF model for `llama-cpp-python` |
| `CHROMA_HOST`     | ChromaDB host                             |
| `CHROMA_PORT`     | ChromaDB port                             |
| `EMBEDDING_MODEL` | SentenceTransformer model name            |

Copy `.env.example` to `.env` and adjust as needed.

## How to run tests

```bash
pip install -r requirements.txt
make test
```

## License

MIT
