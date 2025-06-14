"""Chunk JSONL documents for embedding."""

import json
import logging
import sys
from pathlib import Path


def chunk_text(text: str, size: int = 500) -> list[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), size):
        chunk = " ".join(words[i : i + size])
        chunks.append(chunk)
    return chunks


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: chunk_jsonl.py <input.jsonl> <output.jsonl>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])

    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")
    logging.info("Chunking %s", input_path)

    try:
        with (
            input_path.open("r", encoding="utf-8") as f_in,
            out_path.open("w", encoding="utf-8") as f_out,
        ):
            for line in f_in:
                try:
                    text = json.loads(line)["text"]
                except Exception as exc:
                    logging.error("Invalid JSON line: %s", exc)
                    continue
                for chunk in chunk_text(text):
                    json.dump({"text": chunk}, f_out, ensure_ascii=False)
                    f_out.write("\n")
    except Exception:
        logging.exception("Chunking failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
