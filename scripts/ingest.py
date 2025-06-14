"""Load chunks into ChromaDB."""

import json
import logging
import sys
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")

    if len(sys.argv) != 2:
        print("Usage: ingest.py <chunks.jsonl>")
        sys.exit(1)

    input_path = Path(sys.argv[1])

    client = chromadb.Client()
    collection = client.get_or_create_collection("app-helper")
    embedder = SentenceTransformer("intfloat/multilingual-e5-large")

    try:
        docs = []
        with input_path.open("r", encoding="utf-8") as f:
            for line in f:
                text = json.loads(line)["text"]
                docs.append(text)

        embeddings = embedder.encode(docs)
        for i, doc in enumerate(docs):
            collection.add(documents=[doc], embeddings=[embeddings[i]], ids=[str(i)])
        logging.info("Ingested %d chunks", len(docs))
    except Exception as exc:  # pragma: no cover - error path
        logging.error("Ingestion failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
