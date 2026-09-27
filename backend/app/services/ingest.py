"""Turn uploaded files into searchable chunks: extract -> chunk -> embed -> store."""

import io
import re
from dataclasses import dataclass
from pathlib import Path

import docx
import pypdf

from app.config import settings
from app.services import embeddings, vector_store

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


class UnsupportedFileError(ValueError):
    pass


@dataclass
class TextBlock:
    text: str
    page: int | None


@dataclass
class IngestResult:
    source: str
    chunks: int


def extract_blocks(data: bytes, filename: str) -> list[TextBlock]:
    """Read a file's text. PDFs keep page numbers; other formats have none."""
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFileError(
            f"Unsupported file type '{suffix}'. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    if suffix == ".pdf":
        reader = pypdf.PdfReader(io.BytesIO(data))
        return [
            TextBlock(text=page.extract_text() or "", page=i)
            for i, page in enumerate(reader.pages, start=1)
        ]

    if suffix == ".docx":
        document = docx.Document(io.BytesIO(data))
        text = "\n".join(p.text for p in document.paragraphs)
        return [TextBlock(text=text, page=None)]

    return [TextBlock(text=data.decode("utf-8", errors="replace"), page=None)]


def chunk_text(text: str, *, size: int | None = None, overlap: int | None = None) -> list[str]:
    """Split text into overlapping word windows. Overlap keeps sentences from being cut in half."""
    size = size or settings.chunk_words
    overlap = settings.chunk_overlap_words if overlap is None else overlap
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")

    words = re.sub(r"\s+", " ", text).strip().split(" ")
    if words == [""]:
        return []

    step = size - overlap
    chunks = [" ".join(words[i : i + size]) for i in range(0, len(words), step)]
    # Drop a trailing chunk that the previous window already fully covered.
    if len(chunks) > 1 and len(words) % step <= overlap and len(words) > size:
        chunks.pop()
    return [c for c in chunks if c.strip()]


def ingest_bytes(data: bytes, filename: str) -> IngestResult:
    """Ingest one file, replacing any previously stored version of it."""
    blocks = extract_blocks(data, filename)

    texts: list[str] = []
    pages: list[int | None] = []
    for block in blocks:
        for chunk in chunk_text(block.text):
            texts.append(chunk)
            pages.append(block.page)

    if not texts:
        raise ValueError(f"No readable text found in '{filename}' (is it a scanned PDF?)")

    vector_store.delete_source(filename)
    vectors = embeddings.embed_documents(texts)
    stored = vector_store.add_chunks(
        source=filename, texts=texts, embeddings=vectors, pages=pages
    )
    return IngestResult(source=filename, chunks=stored)


def ingest_path(path: Path) -> IngestResult:
    return ingest_bytes(path.read_bytes(), path.name)


def ingest_directory(directory: Path) -> list[IngestResult]:
    results = []
    for path in sorted(directory.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            results.append(ingest_path(path))
    return results
