"""Extract text from a PDF file and output to JSONL."""

import json
import logging
import sys
from pathlib import Path

from pypdf import PdfReader


def extract_text(pdf_path: Path) -> list[str]:
    """Return the text of each PDF page."""

    try:
        reader = PdfReader(str(pdf_path))
    except Exception as exc:  # pragma: no cover - simple wrapper
        logging.error("Failed to read PDF %s: %s", pdf_path, exc)
        raise

    pages = []
    for i, page in enumerate(reader.pages):
        try:
            pages.append(page.extract_text() or "")
        except Exception as exc:  # pragma: no cover - PDF extraction failure
            logging.error("Failed to extract text from page %s: %s", i, exc)
            pages.append("")
    return pages


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: extract_pdf_text.py <input.pdf> <output.jsonl>")
        sys.exit(1)
    pdf_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])

    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")
    logging.info("Extracting text from %s", pdf_path)

    try:
        texts = extract_text(pdf_path)
    except Exception:
        logging.exception("Extraction failed")
        sys.exit(1)

    logging.info("Writing JSONL to %s", out_path)
    try:
        with out_path.open("w", encoding="utf-8") as f:
            for text in texts:
                json.dump({"text": text}, f, ensure_ascii=False)
                f.write("\n")
    except Exception:
        logging.exception("Failed to write output")
        sys.exit(1)


if __name__ == "__main__":
    main()
