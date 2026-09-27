# RAG Project

Monorepo for a Retrieval-Augmented Generation chat app: ask questions with a plain
LLM, or ground the answers in your own documents.

```
.
├── frontend/   React + Vite chat UI
└── backend/    FastAPI + ChromaDB + DeepSeek
```

## How it works

**Ingestion** (when you upload a document)

```
file → extract text → chunk (200 words, 40 overlap) → embed → store in ChromaDB
```

**Question** (every message)

```
question ─┬─ LLM mode     → DeepSeek → answer
          └─ LLM+RAG mode → embed question → search ChromaDB (top 4)
                          → drop weak matches → prompt with context
                          → DeepSeek → answer + sources
```

Embeddings run locally with `BAAI/bge-small-en-v1.5` (fastembed/ONNX), so only the
chat completion needs an API key. The model downloads once on first use (~130 MB).

## Prerequisites

- Node.js 20+
- Python 3.12+ and [uv](https://docs.astral.sh/uv/)
- A DeepSeek API key ([platform.deepseek.com](https://platform.deepseek.com))

## Setup

```bash
npm run setup                      # frontend (npm workspaces) + backend (uv sync)
cp backend/.env.example backend/.env
# then put your key in backend/.env:  DEEPSEEK_API_KEY=sk-...
```

## Development

```bash
npm run dev       # backend on :8000, frontend on :5173
```

Vite proxies `/api/*` to the backend, so no CORS setup is needed locally.
API docs: http://localhost:8000/docs

| Command | What it does |
| --- | --- |
| `npm run dev` | Start backend + frontend |
| `npm run dev:frontend` / `dev:backend` | Start one of them |
| `npm run build` | Production build of the frontend |
| `npm run lint` | oxlint (frontend) + ruff (backend) |
| `npm run test` | Backend tests (pytest) |
| `npm run ingest` | Index everything in `backend/data/docs/` |
| `npm run docs:list` / `docs:clear` | List or wipe the index |

## Adding documents

Either drop files in the UI (**Docs** button in the header), or put them in
`backend/data/docs/` and run `npm run ingest`. Supported: PDF, DOCX, TXT, MD.
PDF sources keep their page numbers and show up as `report.pdf (p. 7)`.

Re-uploading a file replaces its previous version instead of duplicating it.

## API

| Endpoint | Purpose |
| --- | --- |
| `POST /api/chat` | `{ question, mode }` → `{ answer, sources[] }`; mode is `llm` or `llm_rag` |
| `GET /api/documents` | List indexed documents |
| `POST /api/documents` | Upload one file (multipart, max 20 MB) |
| `DELETE /api/documents/{name}` | Remove a document from the index |
| `GET /api/health` | Status, whether a key is set, number of indexed chunks |

Errors come back as `{ "detail": "..." }`: 503 when the API key is missing or
rejected, 502 when DeepSeek is unreachable, 415/422 for bad uploads.

## Backend layout

| File | Role |
| --- | --- |
| `app/api/chat.py` | Picks the path for each mode |
| `app/api/documents.py` | Upload / list / delete |
| `app/services/ingest.py` | Extract text, chunk, store |
| `app/services/embeddings.py` | Local embedding model |
| `app/services/vector_store.py` | ChromaDB wrapper |
| `app/services/rag.py` | Retrieval |
| `app/services/llm.py` | DeepSeek client + prompts |
| `app/cli.py` | `ingest` / `list` / `clear` commands |

## Tuning

`backend/.env` (see `.env.example`): `CHUNK_WORDS`, `CHUNK_OVERLAP_WORDS`, `TOP_K`,
`MIN_SCORE` (drops weak matches), `DEEPSEEK_MODEL`, `LLM_MAX_TOKENS`.
