"""Chunk JSONL documents for embedding."""
import json
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

    with input_path.open("r", encoding="utf-8") as f_in, out_path.open(
        "w", encoding="utf-8"
    ) as f_out:
        for line in f_in:
            text = json.loads(line)["text"]
            for chunk in chunk_text(text):
                json.dump({"text": chunk}, f_out, ensure_ascii=False)
                f_out.write("\n")


if __name__ == "__main__":
    main()
