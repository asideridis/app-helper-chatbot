# 🧩 App Helper Chatbot

A self‑hosted Retrieval Augmented Generation (RAG) service that lets your team ask Greek questions about any internal application manual and get grounded, Greek answers with citations.

> One deployment - many knowledge bases.  
> Each *app_id* lives in its own Chroma collection, so "ERP", "HR", and "CRM" manuals stay isolated.

---

## Table of contents
1. [Why use it](#why-use-it)
2. [Feature tour](#feature-tour)
3. [Quick start (Docker Compose)](#quick-start-docker-compose)
4. [Manual setup](#manual-setup)
5. [Ingesting documents](#ingesting-documents)
6. [API reference](#api-reference)
7. [Environment variables](#environment-variables)
8. [Running tests](#running-tests)
9. [Production deployment](#production-deployment)
10. [FAQ](#faq)
11. [License](#license)

---

## Why use it

* **Greek in - Greek out.** Meltemi 7B guarantees fluent Greek and solid technical vocabulary.  
* **App‑scoped privacy.** Each application's docs are stored in its own namespace, so users never leak info across products.  
* **Offline friendly.** Runs fully on‑prem: ChromaDB for vectors, Ollama for GGUF models, FastAPI for the API.  
* **Works everywhere.** Spin it up with Docker Compose in dev, drop the same image behind systemd in prod.  

---

## Feature tour

| Category          | Details                                                |
|-------------------|--------------------------------------------------------|
| Language model    | Meltemi‑7B‑Instruct (`llama‑cpp‑python` via Ollama)    |
| Embeddings        | `intfloat/multilingual-e5-large` (replaceable)         |
| Vector store      | ChromaDB (persistent on volume)                        |
| API               | FastAPI 0.110 - endpoints `/chat/{app_id}`, `/healthz` |
| Auth              | Static token in `X-API-Token` header                   |
| Rate limiting     | 60 reqs per minute per IP (configurable)               |
| Citations         | Each answer lists source file and page number          |
| Tests             | Pytest unit + integration                              |

---

## Quick start (Docker Compose)

```bash
# clone and enter the repo
git clone https://github.com/asideridis/app-helper-chatbot.git
cd app-helper-chatbot

# bring up Chroma, Ollama and the API
make compose-up

# run API with autoreload for live dev
make dev   # http://localhost:8080
```

Under the hood Compose pulls the Meltemi model into `/ollama/models` on first run - grab a coffee.

---

## Manual setup

Prefer a bare‑metal install?  

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# download model once
./scripts/download_model.sh     # or supply your own MODEL_URL

# launch the API
uvicorn app.rag_api:app --host 0.0.0.0 --port 8080
```

---

## Ingesting documents

```bash
python scripts/ingest.py   --app-id erp   --path docs/ERP_Manual.pdf   --chunk-size 400   --overlap 60
```

* `app-id` - folder (collection) in Chroma  
* `chunk-size` & `overlap` - tune for recall vs speed  

Run the command again any time the manual changes - chunks for that *app_id* are upserted.

---

## API reference

### `POST /chat/{app_id}`

| Field      | Type   | Description                     |
|------------|--------|---------------------------------|
| `question` | string | Greek user question             |

Returns:

```json
{
  "answer": "…",
  "citations": [
    {"file": "ERP_Manual.pdf", "page": 12}
  ]
}
```

### `GET /healthz`

200 if the embedder and LLM respond inside 2 seconds. Used by Docker Compose's healthcheck and systemd.

---

## Environment variables

| Var                 | Default                    | Role                                   |
|---------------------|----------------------------|----------------------------------------|
| `CHATBOT_API_TOKEN` | `secret-token`             | Required header on `/chat/*`           |
| `MODEL_NAME`        | `meltemi-7b-instruct`      | GGUF tag or path for Ollama            |
| `CHROMA_HOST`       | `chromadb` (Compose)       | Hostname for Chroma                    |
| `CHROMA_PORT`       | `8000`                     | Port for Chroma                        |
| `EMBEDDING_MODEL`   | `intfloat/multilingual-e5-large` | Name compatible with SentenceTransformers |

Copy `.env.example` to `.env` and tweak as needed.

---

## Running tests

```bash
make test          # runs pytest with coverage
```

---

## Production deployment

Compose is fine for small teams. For a long‑running service:

1. Build the image: `docker build -t app-helper:latest .`  
2. Copy it and your `.env` file to the server.  
3. Use the sample unit below.

```ini
# /etc/systemd/system/app-helper.service
[Unit]
Description=App Helper Chatbot
After=network.target

[Service]
ExecStart=/usr/bin/docker run --rm --env-file /opt/app-helper/.env -p 8080:8080 app-helper:latest
Restart=always
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now app-helper
```

---

## FAQ

**How big can my PDFs be?**  
Chroma and Meltemi handle thousands of pages, but start with 400‑token chunks for best recall.

**Can it speak English?**  
Yes - change the system prompt, but Meltemi is tuned for Greek so quality drops a bit.

**Is the API public?**  
No. It expects a static token and has no user management. Put it behind your own auth proxy if needed.

---

## License

MIT
