"""Load chunks into ChromaDB."""

import json
import logging
import sys
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: ingest.py <chunks.jsonl>")
        sys.exit(1)

    input_path = Path(sys.argv[1])

    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")
    logging.info("Loading chunks from %s", input_path)

    try:
        client = chromadb.Client()
        collection = client.get_or_create_collection("app-helper")
        embedder = SentenceTransformer("intfloat/multilingual-e5-large")
    except Exception:
        logging.exception("Failed to initialize components")
        sys.exit(1)

    docs = []
    try:
        with input_path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    text = json.loads(line)["text"]
                except Exception as exc:
                    logging.error("Invalid JSON line: %s", exc)
                    continue
                docs.append(text)
    except Exception:
        logging.exception("Failed to read chunks")
        sys.exit(1)

    try:
        embeddings = embedder.encode(docs)
        for i, doc in enumerate(docs):
            collection.add(documents=[doc], embeddings=[embeddings[i]], ids=[str(i)])
    except Exception:
        logging.exception("Failed to store embeddings")
        sys.exit(1)


if __name__ == "__main__":
    main()
