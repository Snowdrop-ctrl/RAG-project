"""Retrieval: embed the question, then find the closest chunks in the vector store."""

from dataclasses import dataclass

from app.config import settings
from app.services import embeddings, vector_store


@dataclass
class Chunk:
    text: str
    source: str
    page: int | None = None
    score: float = 0.0

    @property
    def label(self) -> str:
        return f"{self.source} (p. {self.page})" if self.page else self.source


async def retrieve(question: str, top_k: int | None = None) -> list[Chunk]:
    """Return the most relevant chunks for a question, weakest matches dropped."""
    if vector_store.count() == 0:
        return []

    query_vector = embeddings.embed_query(question)
    hits = vector_store.search(query_vector, top_k or settings.top_k)
    return [
        Chunk(text=h.text, source=h.source, page=h.page, score=h.score)
        for h in hits
        if h.score >= settings.min_score
    ]
