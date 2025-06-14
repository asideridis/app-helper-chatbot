# App Helper Chatbot

A local RAG-based chatbot that answers technical questions in Greek using PDF manuals as context.

## Project Structure

- `app/` – FastAPI application
- `scripts/` – CLI helpers for preparing and ingesting data

## Quickstart

1. Install dependencies:

   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Run the API:

   ```bash
   uvicorn app.rag_api:app --reload
   ```

3. Ingest your PDFs using the scripts in `scripts/`.
