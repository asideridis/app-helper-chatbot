"""CLI tool to load PDF text into ChromaDB."""

from __future__ import annotations

import logging
from pathlib import Path

from pypdf import PdfReader

from app.retriever import add_documents

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")


def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    words = text.split()
    step = max(size - overlap, 1)
    chunks = []
    for i in range(0, len(words), step):
        chunk = " ".join(words[i : i + size])
        chunks.append(chunk)
    return chunks


def extract_pages(path: Path) -> list[tuple[str, int]]:
    reader = PdfReader(str(path))
    pages = []
    for idx, page in enumerate(reader.pages, 1):
        pages.append((page.extract_text() or "", idx))
    return pages


def load_pdf(app_id: str, pdf_path: Path, size: int, overlap: int) -> int:
    count = 0
    for text, page_no in extract_pages(pdf_path):
        for chunk in chunk_text(text, size, overlap):
            meta = {"source": f"{pdf_path.name}#page={page_no}"}
            add_documents(app_id, [(chunk, meta)])
            count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--app-id", required=True)
    parser.add_argument("--path", required=True)
    parser.add_argument("--chunk-size", type=int, default=400)
    parser.add_argument("--overlap", type=int, default=50)
    args = parser.parse_args()

    target = Path(args.path)
    if target.is_file():
        files = [target]
    else:
        files = list(target.glob("*.pdf"))
    total = 0
    for file in files:
        total += load_pdf(args.app_id, file, args.chunk_size, args.overlap)
    logging.info("Loaded %d chunks", total)


if __name__ == "__main__":
    main()
