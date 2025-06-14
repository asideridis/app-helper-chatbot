"""Extract text from a PDF file and output to JSONL."""

import json
import logging
import sys
from pathlib import Path

from pypdf import PdfReader


def extract_text(pdf_path: Path) -> list[str]:
    try:
        reader = PdfReader(str(pdf_path))
    except Exception as exc:  # pragma: no cover - PDF read errors are rare
        logging.error("Failed to open %s: %s", pdf_path, exc)
        raise

    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return pages


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")

    if len(sys.argv) != 3:
        print("Usage: extract_pdf_text.py <input.pdf> <output.jsonl>")
        sys.exit(1)
    pdf_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])

    try:
        texts = extract_text(pdf_path)
        with out_path.open("w", encoding="utf-8") as f:
            for text in texts:
                json.dump({"text": text}, f, ensure_ascii=False)
                f.write("\n")
        logging.info("Wrote %d pages to %s", len(texts), out_path)
    except Exception as exc:  # pragma: no cover - error path
        logging.error("Extraction failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
