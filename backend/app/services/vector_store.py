"""Chroma-backed vector store. Persists to disk under settings.chroma_dir."""

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import chromadb
from chromadb.errors import NotFoundError

from app.config import settings

COLLECTION = "documents"


@dataclass
class StoredChunk:
    text: str
    source: str
    page: int | None
    score: float


@lru_cache(maxsize=1)
def _collection() -> chromadb.api.models.Collection.Collection:
    Path(settings.chroma_dir).mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=settings.chroma_dir)
    return client.get_or_create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})


def add_chunks(
    *,
    source: str,
    texts: list[str],
    embeddings: list[list[float]],
    pages: list[int | None],
) -> int:
    if not texts:
        return 0
    _collection().add(
        ids=[f"{source}::{i}" for i in range(len(texts))],
        documents=texts,
        embeddings=embeddings,
        metadatas=[{"source": source, "page": p if p is not None else -1} for p in pages],
    )
    return len(texts)


def search(embedding: list[float], top_k: int) -> list[StoredChunk]:
    if count() == 0:
        return []
    res = _collection().query(
        query_embeddings=[embedding],
        n_results=min(top_k, count()),
        include=["documents", "metadatas", "distances"],
    )
    chunks: list[StoredChunk] = []
    for text, meta, distance in zip(
        res["documents"][0], res["metadatas"][0], res["distances"][0], strict=True
    ):
        page = meta.get("page", -1)
        chunks.append(
            StoredChunk(
                text=text,
                source=str(meta.get("source", "unknown")),
                page=None if page in (-1, None) else int(page),
                # Cosine distance (0 = identical) converted to a 0-1 similarity score.
                score=max(0.0, 1.0 - float(distance)),
            )
        )
    return chunks


def count() -> int:
    return _collection().count()


def list_sources() -> list[dict[str, object]]:
    res = _collection().get(include=["metadatas"])
    counts: dict[str, int] = {}
    for meta in res["metadatas"]:
        name = str(meta.get("source", "unknown"))
        counts[name] = counts.get(name, 0) + 1
    return [{"source": s, "chunks": c} for s, c in sorted(counts.items())]


def delete_source(source: str) -> int:
    existing = _collection().get(where={"source": source}, include=[])
    removed = len(existing["ids"])
    if removed:
        _collection().delete(ids=existing["ids"])
    return removed


def reset() -> None:
    """Drop every chunk. Used by tests and the `clear` CLI command."""
    client = chromadb.PersistentClient(path=settings.chroma_dir)
    try:
        client.delete_collection(COLLECTION)
    except NotFoundError:  # nothing indexed yet
        pass
    _collection.cache_clear()
