# 🧩 Project Overview
A private Retrieval-Augmented Generation (RAG) chatbot built for internal use at a bank.

**Purpose:** help users understand how internal banking applications work by querying PDF-based manuals.

All answers are in Greek and strictly grounded in the ingested documents.

## ⚙️ Features
- FastAPI backend with `/chat` endpoint
- API token authentication via `X-API-Token` header
- Basic in-memory rate limiting
- Simple retrieval from ChromaDB using sentence-transformer embeddings
- Embedding model: `intfloat/multilingual-e5-large`
- Language model: Meltemi 7B Instruct (GGUF) running via `llama-cpp-python`
- Vector store: ChromaDB (local, persisted)
- Chunked PDF ingestion pipeline
- Greek-only responses with zero tolerance for hallucination

## 🧪 Project Structure
```
.
├── app/
│   └── rag_api.py            # FastAPI app with RAG chain
├── scripts/
│   ├── extract_pdf_text.py   # Extracts Greek text from PDFs
│   ├── chunk_jsonl.py        # Splits long text into overlapping chunks
│   ├── ingest.py             # Embeds and loads chunks into ChromaDB
│   └── download_model.sh     # Downloads Meltemi 7B GGUF model
├── requirements.txt
├── pyproject.toml
└── README.md
```

## 🛠️ Setup
1. Ensure Python 3.11+ is installed.
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. (Optional) Download the Meltemi model:
   ```bash
   bash scripts/download_model.sh
   ```
5. Export `CHATBOT_API_TOKEN` with your preferred token before launching the server.

## 🚀 How to Use
1. Place PDF manuals inside a `pdfs/` directory.
2. Run the pipeline:
   ```bash
   python scripts/extract_pdf_text.py pdfs/ output.jsonl
   python scripts/chunk_jsonl.py output.jsonl chunks.jsonl
   python scripts/ingest.py chunks.jsonl
   ```
3. Start the FastAPI server:
   ```bash
   uvicorn app.rag_api:app --reload
   ```
4. Query it (requires an API token):
   ```bash
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -H "X-API-Token: <your-token>" \
     -d '{"question":"Πώς κάνω εισαγωγή αιτημάτων μαζικά;"}'
   ```

## 🧠 System Prompt
```
Είσαι ο App Helper, ένας έμπειρος βοηθός που εξηγεί πώς λειτουργεί η εφαρμογή και οι διαδικασίες.
Απαντάς πάντοτε στα Ελληνικά, με σαφή βήματα όπου χρειάζεται, και χρησιμοποιείς ΜΟΝΟ τις πληροφορίες που βρίσκονται στο πλαίσιο «context».
Αν το context είναι άδειο ή δεν περιέχει σαφή πληροφορία για την ερώτηση, πες ξεκάθαρα: «Δεν βρέθηκε σχετική πληροφορία».
```

## 📦 Dependencies
See `requirements.txt` and `pyproject.toml`. Install with:
```bash
pip install -r requirements.txt
```

## ⚠️ Notes
- Vector DB is stored at: `~/chatbot/chroma`
- Model file is expected at: `~/models/meltemi7b.q4km.gguf`
- This repo is offline-ready, designed for air-gapped environments
- All responses are restricted to PDF context only
- Set `CHATBOT_API_TOKEN` to control the required API token
- Licensed under the MIT License
