# RAG Project

Monorepo for a Retrieval-Augmented Generation chat app.

```
.
├── frontend/   React + Vite chat UI
└── backend/    FastAPI API (Python, managed with uv)
```

## Prerequisites

- Node.js 20+
- Python 3.12+ and [uv](https://docs.astral.sh/uv/)

## Setup

```bash
npm run setup     # installs frontend (npm workspaces) + backend (uv sync)
```

## Development

```bash
npm run dev       # runs backend on :8000 and frontend on :5173
```

Vite proxies `/api/*` to the backend, so no CORS or env config is needed locally.
API docs: http://localhost:8000/docs

| Command                | What it does                     |
| ---------------------- | -------------------------------- |
| `npm run dev`          | Start backend + frontend         |
| `npm run dev:frontend` | Frontend only                    |
| `npm run dev:backend`  | Backend only                     |
| `npm run build`        | Production build of the frontend |
| `npm run lint`         | oxlint (frontend) + ruff (backend) |
| `npm run test`         | Backend tests (pytest)           |

## API

`POST /api/chat`

```json
{ "question": "What is RAG?", "mode": "llm_rag" }
```

`mode` is `llm` (model only) or `llm_rag` (retrieve context, then answer).

```json
{ "answer": "...", "sources": ["doc.pdf"] }
```

## Where to build the RAG pipeline

- `backend/app/services/rag.py`: retrieval (embeddings + vector store)
- `backend/app/services/llm.py`: LLM calls
- `backend/app/api/chat.py`: request flow for each mode

Both services currently return placeholder data.
