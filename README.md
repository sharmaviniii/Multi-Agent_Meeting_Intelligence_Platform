# Multi-Agent Meeting Intelligence Platform

Phase 1 implements a working meeting intelligence MVP:

- FastAPI service
- MeetingBank downloader and ingestion pipeline
- Transcript normalization
- Chunking
- Embedding generation with `BAAI/bge-small-en-v1.5`
- ChromaDB integration using the single `meeting_memory` collection
- GPT-4o-mini summarization
- Offline development mode with mock LLM and mock embeddings

Later phases will add PostgreSQL, CrewAI, LangGraph, AutoGen, Docker, LangSmith, and GitHub Actions after approval.

## Local Setup

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -e ".[dev]"
Copy-Item .env.example .env
```

By default, `.env.example` sets:

```text
OFFLINE_MODE=true
```

Offline mode:

- Does not call OpenAI.
- Does not require ChromaDB.
- Does not download the local embedding model.
- Uses deterministic mock embeddings and mock summaries.
- Lets unit tests run without external services.

## Run API Locally

```powershell
uvicorn meeting_intel.api.app:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Phase 1 Endpoints

### POST /upload

```json
{
  "title": "Demo Meeting",
  "source_type": "raw_text",
  "participants": ["Asha", "Rahul"],
  "text": "Asha: We need the demo ready by Friday.\nRahul: I will finish the API."
}
```

### POST /summarize

Summarize by text:

```json
{
  "title": "Demo Meeting",
  "text": "Asha: We need the demo ready by Friday.\nRahul: I will finish the API."
}
```

Summarize a previously uploaded meeting:

```json
{
  "meeting_id": "uuid-from-upload"
}
```

### POST /ask

```json
{
  "question": "Who is finishing the API?",
  "meeting_id": "uuid-from-upload",
  "top_k": 5
}
```

### POST /ingest/meetingbank

In offline mode this ingests a deterministic MeetingBank-style sample.

If `OFFLINE_MODE=false` and `MEETINGBANK_URL` is set, the downloader fetches that JSON or JSONL dataset file.

## MeetingBank Ingestion

Run:

```powershell
python scripts\\ingest_meetingbank.py
```

The loader accepts JSONL or JSON records with common MeetingBank-style fields:

- `id`
- `title`
- `transcript`
- `meeting_transcript`
- `text`
- `dialogue`
- `summary`
- `reference_summary`

All records normalize into:

```json
{
  "meeting_id": "",
  "title": "",
  "date": "",
  "participants": [],
  "transcript": [],
  "summary": "",
  "action_items": [],
  "decisions": [],
  "risks": [],
  "follow_ups": [],
  "embeddings_metadata": {}
}
```

## ChromaDB Mode

Set:

```text
OFFLINE_MODE=false
CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_COLLECTION=meeting_memory
OPENAI_API_KEY=...
```

Then run a ChromaDB server separately. Phase 1 intentionally does not add Docker.

## Tests

```powershell
pytest
```

The tests use offline mode and do not require OpenAI, ChromaDB, PostgreSQL, Docker, CrewAI, AutoGen, LangGraph, or LangSmith.
