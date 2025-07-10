# App Helper Chatbot

A multilingual RAG service that replies only in Greek. It supports many
applications, each stored in its own Chroma collection.

## Quick start

```bash
make compose-up      # start api, chromadb and ollama
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
  -d '{"question": "Τί είναι ERP;"}'
```

The JSON response includes `answer` and `citations`.

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
make test
```

## License

MIT
