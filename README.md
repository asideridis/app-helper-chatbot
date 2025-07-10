# App Helper Chatbot

A retrieval augmented generation service built with FastAPI, Chroma
and `llama-cpp-python`. The API can host many applications, each using
its own document collection. Answers are returned in Greek unless the
question is in English.

## Quick start

1. Copy `.env.example` to `.env` and adjust paths if needed.
2. Run:

   ```bash
   make compose-up      # start Chroma, Ollama and the API
   make dev             # run the API with autoreload on localhost:8080
   ```

### Ingest documents

```bash
python scripts/ingest.py --app-id my_app \
  --path docs/manual.pdf --chunk-size 400 --overlap 50
```

### Query the API

```bash
curl -X POST http://localhost:8080/chat/my_app \
  -H 'Content-Type: application/json' \
  -H 'X-API-Token: secret-token' \
  -d '{"question": "Τί είναι ERP;"}'
```

The response includes an `answer` field and a list of `citations`.

## Environment variables

| Name            | Purpose                                  |
|-----------------|-------------------------------------------|
| `MODEL_NAME`    | Path to GGUF model for `llama-cpp-python` |
| `CHROMA_HOST`   | ChromaDB host                             |
| `CHROMA_PORT`   | ChromaDB port                             |
| `EMBEDDING_MODEL` | SentenceTransformer model name          |

Copy `.env.example` to `.env` and edit as needed.

## How to run tests

```bash
pip install -r requirements.txt
make test
```

## License

MIT
