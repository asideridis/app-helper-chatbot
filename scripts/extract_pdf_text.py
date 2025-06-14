"""Extract text from a PDF file and output to JSONL."""

import json
import sys
from pathlib import Path

from pypdf import PdfReader


def extract_text(pdf_path: Path) -> list[str]:
    reader = PdfReader(str(pdf_path))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return pages


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: extract_pdf_text.py <input.pdf> <output.jsonl>")
        sys.exit(1)
    pdf_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])

    texts = extract_text(pdf_path)
    with out_path.open("w", encoding="utf-8") as f:
        for text in texts:
            json.dump({"text": text}, f, ensure_ascii=False)
            f.write("\n")


if __name__ == "__main__":
    main()
