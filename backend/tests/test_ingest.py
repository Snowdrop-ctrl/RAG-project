import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import ingest, vector_store

client = TestClient(app)


def test_chunk_text_splits_with_overlap():
    words = " ".join(str(i) for i in range(500))
    chunks = ingest.chunk_text(words, size=100, overlap=20)
    assert len(chunks) > 1
    assert all(len(c.split()) <= 100 for c in chunks)
    # Consecutive chunks share their overlap region.
    assert chunks[0].split()[-20:] == chunks[1].split()[:20]


def test_chunk_text_handles_short_and_empty_input():
    assert ingest.chunk_text("") == []
    assert ingest.chunk_text("   \n  ") == []
    assert ingest.chunk_text("one short sentence") == ["one short sentence"]


def test_extract_rejects_unsupported_type():
    with pytest.raises(ingest.UnsupportedFileError):
        ingest.extract_blocks(b"data", "photo.png")


def test_upload_list_and_delete_roundtrip(clean_index):
    res = client.post(
        "/api/documents",
        files={"file": ("notes.md", b"# Title\n\nSome useful content about pandas.", "text/markdown")},
    )
    assert res.status_code == 201
    assert res.json()["chunks"] == 1

    listing = client.get("/api/documents").json()
    assert listing["documents"] == [{"source": "notes.md", "chunks": 1}]
    assert listing["total_chunks"] == 1

    assert client.delete("/api/documents/notes.md").status_code == 204
    assert client.get("/api/documents").json()["documents"] == []
    assert vector_store.count() == 0


def test_reupload_replaces_previous_version(clean_index):
    files = {"file": ("doc.txt", b"first version of the text", "text/plain")}
    client.post("/api/documents", files=files)
    client.post("/api/documents", files={"file": ("doc.txt", b"second version of the text", "text/plain")})

    listing = client.get("/api/documents").json()
    assert listing["total_chunks"] == 1  # not duplicated


def test_upload_rejects_unsupported_type(clean_index):
    res = client.post("/api/documents", files={"file": ("photo.png", b"\x89PNG", "image/png")})
    assert res.status_code == 415


def test_upload_rejects_empty_file(clean_index):
    res = client.post("/api/documents", files={"file": ("empty.txt", b"   ", "text/plain")})
    assert res.status_code == 422


def test_delete_unknown_document_returns_404(clean_index):
    assert client.delete("/api/documents/nope.txt").status_code == 404
