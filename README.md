# Multi-Agent Meeting Intelligence Platform

The platform currently implements a working meeting intelligence MVP:

- FastAPI service
- MeetingBank downloader and ingestion pipeline
- Transcript normalization
- Chunking
- Embedding generation with OpenAI `text-embedding-3-small`
- ChromaDB integration using the single `meeting_memory` collection
- GPT-4o-mini summarization
- Offline development mode with mock LLM and mock embeddings
- Structured meeting intelligence endpoints for actions, decisions, risks, and follow-up email drafts
- Optional PostgreSQL persistence with Alembic migrations

Later phases will add CrewAI, LangGraph, AutoGen, LangSmith, and GitHub Actions after approval.

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

Production mode:

- Set `OFFLINE_MODE=false`.
- Set `OPENAI_API_KEY` to enable GPT-4o-mini calls.
- Set `JWT_SECRET` to require bearer JWT authentication on protected endpoints.
- Uses `OPENAI_MODEL=gpt-4o-mini` by default.
- Uses OpenAI `text-embedding-3-small` embeddings in production and deterministic mock embeddings offline.
- Stores and retrieves vectors from the configured ChromaDB collection.

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
CHROMA_PATH=./chroma
CHROMA_COLLECTION=meeting_memory
OPENAI_API_KEY=...
```

The API uses `chromadb.PersistentClient` and creates the directory automatically. In Docker Compose, ChromaDB is persistent through the `chroma_data` volume mounted at `/app/chroma`. On Render, set `CHROMA_PATH` to the mounted persistent disk path.

## PostgreSQL Persistence

Offline mode continues to use the in-memory repository and does not require PostgreSQL.

To use PostgreSQL persistence, install the project dependencies, set:

```text
OFFLINE_MODE=false
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/meeting_intel
```

Then run migrations:

```powershell
alembic upgrade head
```

Alembic migration files live in `alembic/versions`.

## Docker Compose

The Compose stack includes:

- FastAPI API container
- PostgreSQL container
- ChromaDB container

By default, the API still starts with `OFFLINE_MODE=true`, so it uses mock LLM responses,
mock embeddings, and in-memory meeting persistence.

Run:

```powershell
docker compose up --build
```

Open:

```text
http://127.0.0.1:8000/docs
```

To use PostgreSQL persistence in the Docker stack, set `OFFLINE_MODE=false` and run:

```powershell
docker compose exec api alembic upgrade head
```

The API container uses this default database URL:

```text
postgresql+psycopg://meeting_intel:meeting_intel@postgres:5432/meeting_intel
```

ChromaDB persistence is embedded in the API process through `chromadb.PersistentClient`. Compose mounts `chroma_data` at `/app/chroma`; production deployments can override this with `CHROMA_PATH`.

## Security And Operations

When `OFFLINE_MODE=false`, protected endpoints require a bearer JWT signed with
`JWT_SECRET`. Tokens must include an `exp` claim. Offline mode keeps authentication optional
for local development and tests.

Rate limiting applies to:

- `POST /upload`
- `POST /summarize`
- `POST /ask`
- `POST /action-items`
- `POST /decisions`
- `POST /risks`
- `POST /email-draft`

Configure rate limits with:

```text
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW_SECONDS=60
```

Operational endpoints:

- `GET /health`
- `GET /ready`
- `GET /live`
- `GET /metrics`

## Tests

```powershell
pytest
```

The tests use offline mode and do not require OpenAI, ChromaDB, PostgreSQL, Docker, CrewAI, AutoGen, LangGraph, or LangSmith.
