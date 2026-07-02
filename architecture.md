# IntelMeet Architecture

Version: 1.0
Status: Production MVP
Branch: main

---

# 1. Project Overview

IntelMeet is a multi-agent meeting intelligence platform that transforms meeting transcripts and recordings into structured business intelligence.

The platform extracts:

- Transcript
- Executive Summary
- Action Items
- Decisions
- Risks
- Follow-up Email Drafts

The system is designed to evolve into a collaborative SaaS platform with:

- Workspaces
- Teams
- Authentication
- RBAC
- Shared meeting repositories
- Streaming AI responses
- Real-time collaboration

---

# 2. Technology Stack

## Backend

- FastAPI
- SQLAlchemy
- Alembic
- LangGraph
- ChromaDB
- OpenAI API
- Pydantic v2
- Uvicorn
- Python 3.11+

## Frontend

- React 19
- TypeScript
- Vite
- TailwindCSS v4
- shadcn/ui
- React Router
- Axios
- Zod
- TanStack Query

## Infrastructure

- Docker
- Docker Compose
- GitHub Actions
- Pytest
- Ruff

---

# 3. High Level Architecture

┌──────────────────────┐
│ React Frontend       │
│ localhost:5173       │
└─────────┬────────────┘
          │ HTTP REST
          ▼
┌──────────────────────┐
│ FastAPI API Layer    │
│ localhost:8000       │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│ Service Layer        │
│ Business Logic       │
└─────────┬────────────┘
          │
 ┌────────┼────────┐
 ▼                 ▼
LangGraph       SQLAlchemy
Workflow        Persistence Layer

 ▼                 ▼
OpenAI API      SQLite/Postgres

 ▼
ChromaDB Vector Store

---

# 4. Request Flow

## Upload Flow

Frontend
    ↓
POST /upload
    ↓
FastAPI Route
    ↓
Upload Service
    ↓
Meeting Creation
    ↓
LangGraph Pipeline
    ↓
OpenAI Processing
    ↓
Persist Results
    ↓
Return Meeting Metadata

Response:

{
    "meeting_id": "...",
    "title": "...",
    "status": "completed"
}

---

## Workspace Flow

Frontend stores:

- meetingId
- title
- timestamp
- status

After upload completes:

Workspace opens.

Each tab fetches independently.

Transcript Tab
    GET /transcript/{meeting_id}

Summary Tab
    GET /summary/{meeting_id}

Action Items Tab
    GET /action-items/{meeting_id}

Decisions Tab
    GET /decisions/{meeting_id}

Risks Tab
    GET /risks/{meeting_id}

Email Draft Tab
    GET /email-draft/{meeting_id}

---

## Cancellation Flow

Each request owns:

AbortController

User navigates away
        ↓
Request cancelled
        ↓
No stale state updates

---

# 5. Frontend Architecture

frontend/
│
├── src/app
├── src/components
├── src/features
├── src/services
├── src/types
└── src/lib

## Feature Modules

upload/
meeting-workspace/
transcript/
summary/
action-items/
decisions/
risks/
email-draft/

---

## API Layer

Location:

src/services/api.ts

Responsibilities:

- Axios wrapper
- Request IDs
- Error normalization
- Zod validation
- Response parsing
- Cancellation support

---

## Request State Machine

Every tab follows:

idle
loading
success
empty
error

No component may bypass this lifecycle.

---

# 6. Backend Architecture

src/meeting_intel/

## Layers

api/
services/
repositories/
models/
schemas/
workflows/
agents/

---

## API Layer

Responsibilities:

- Validation
- Serialization
- Status codes
- Request IDs

No business logic allowed.

---

## Service Layer

Responsibilities:

- Meeting orchestration
- AI execution
- Data transformation
- Workflow execution

---

## Repository Layer

Responsibilities:

- Database operations
- Persistence abstraction
- Query composition

---

## Workflow Layer

Responsibilities:

- LangGraph orchestration
- Agent routing
- State transitions

---

# 7. LangGraph Workflow

Upload
 ↓
Transcription
 ↓
Chunking
 ↓
Embedding Generation
 ↓
Retrieval Context
 ↓
Summary Agent
 ↓
Action Agent
 ↓
Decision Agent
 ↓
Risk Agent
 ↓
Email Agent
 ↓
Persistence

---

# 8. Database Schema

Current Entities

## Meeting

Stores:

- meeting_id
- title
- upload timestamp
- status
- metadata

---

## Transcript Chunk

Stores:

- chunk_id
- meeting_id
- content
- chunk_index

Relationship:

Meeting 1 → N TranscriptChunks

---

## Embedding

Stores:

- embedding_id
- chunk_id
- vector_id
- metadata

Relationship:

TranscriptChunk 1 → 1 Embedding

---

## Future Tables

User
Workspace
WorkspaceMember
Role
Permission
Invitation
AuditLog

---

# 9. Vector Database

Provider:

ChromaDB

Responsibilities:

- Semantic retrieval
- Context augmentation
- RAG support

Constraints:

- Never replace ChromaDB.
- Existing collections must remain compatible.

---

# 10. API Contracts

## POST /upload

Accepts:

- multipart/form-data
- JSON payload

Returns:

{
    "meeting_id": "uuid",
    "title": "meeting title",
    "status": "completed"
}

---

## GET /transcript/{meeting_id}

Returns transcript data.

---

## GET /summary/{meeting_id}

Returns:

- executive summary
- participants
- metadata

---

## GET /action-items/{meeting_id}

Returns:

[
    {
        "owner": "",
        "task": "",
        "deadline": ""
    }
]

---

## GET /decisions/{meeting_id}

Returns decision list.

---

## GET /risks/{meeting_id}

Returns identified risks.

---

## GET /email-draft/{meeting_id}

Returns generated email draft.

---

# 11. Error Handling

Frontend distinguishes:

- Network errors
- Validation errors
- 4xx responses
- 5xx responses
- Cancelled requests
- Malformed responses

All API responses pass through Zod validation.

---

# 12. CORS Policy

Allowed Origins:

http://localhost:5173

Wildcard CORS is prohibited.

---

# 13. Deployment Model

## Local Development

Frontend:

npm run dev

Runs on:

localhost:5173

Backend:

uvicorn app:app --reload

Runs on:

localhost:8000

---

## Docker

Docker exists for:

- CI
- Deployment
- Reproducibility

Docker is NOT mandatory for local development.

---

## Production (Planned)

Frontend
↓
Vercel

Backend
↓
Render / Railway / Fly.io

Database
↓
PostgreSQL

Vector DB
↓
Persistent Chroma

Background Jobs
↓
Celery + Redis

---

# 14. Testing Strategy

Backend:

pytest

Current Status:

34 tests passing

Frontend:

- typecheck passing
- production build passing

---

# 15. Development Constraints

The following rules are mandatory.

## Architecture Rules

- Never rewrite working modules.
- Never replace FastAPI.
- Never replace React.
- Never remove LangGraph.
- Never replace ChromaDB.
- Preserve API compatibility.
- Extend existing modules before creating new ones.
- Prefer migrations over destructive changes.

---

## Git Rules

Branch:

main

Development Style:

Small PR-sized changes.

Maximum Scope:

One subsystem per iteration.

Avoid:

- Massive refactors
- Multi-thousand-line diffs
- Architecture rewrites

---

# 16. Future Roadmap

Phase 2

- Authentication
- User accounts
- RBAC
- Workspaces
- Invitations

Phase 3

- Redis
- Celery
- Background processing
- WebSockets
- Streaming AI

Phase 4

- Multi-tenancy
- Billing
- Subscription management
- Usage quotas
- Analytics

---

# 17. AI Assistant Rules

When AI tools modify this repository:

- Read ARCHITECTURE.md first.
- Treat this document as source of truth.
- Never violate architectural constraints.
- Prefer extension over replacement.
- Keep changes backward compatible.