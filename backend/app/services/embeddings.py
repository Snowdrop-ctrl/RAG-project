"""Local embedding model (ONNX, no API key needed).

The model is loaded lazily and cached, so the first call pays the load cost once.
"""

from functools import lru_cache

from fastembed import TextEmbedding

from app.config import settings


@lru_cache(maxsize=1)
def _model() -> TextEmbedding:
    return TextEmbedding(settings.embedding_model)


def embed_documents(texts: list[str]) -> list[list[float]]:
    return [v.tolist() for v in _model().embed(texts)]


def embed_query(text: str) -> list[float]:
    # bge models expect this prefix on the query side only.
    prefixed = f"Represent this sentence for searching relevant passages: {text}"
    return next(iter(_model().query_embed([prefixed]))).tolist()
