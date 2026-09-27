from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from app.config import settings
from app.services import vector_store

app = FastAPI(title="RAG Project API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["health"])
async def health() -> dict[str, object]:
    return {
        "status": "ok",
        "llm_configured": bool(settings.deepseek_api_key),
        "indexed_chunks": vector_store.count(),
    }


app.include_router(chat_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
