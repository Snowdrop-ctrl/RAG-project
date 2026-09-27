import asyncio
import io

import docx
import pytest
from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas

from app.main import app
from app.services import ingest, rag, vector_store

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


def _make_pdf(pages: list[str]) -> bytes:
    """Build a small multi-page PDF in memory for the extraction tests."""
    buf = io.BytesIO()
    pdf = canvas.Canvas(buf)
    for text in pages:
        pdf.drawString(72, 720, text)
        pdf.showPage()
    pdf.save()
    return buf.getvalue()


def _make_docx(paragraphs: list[str]) -> bytes:
    document = docx.Document()
    for p in paragraphs:
        document.add_paragraph(p)
    buf = io.BytesIO()
    document.save(buf)
    return buf.getvalue()


def test_pdf_extraction_keeps_page_numbers():
    blocks = ingest.extract_blocks(_make_pdf(["First page text", "Second page text"]), "report.pdf")
    assert [b.page for b in blocks] == [1, 2]
    assert "Second page text" in blocks[1].text


def test_pdf_upload_reports_page_in_source_label(clean_index):
    pdf = _make_pdf(["Nothing here.", "The Orion engine delivers 92 kilonewtons of thrust."])
    assert client.post("/api/documents", files={"file": ("engine.pdf", pdf, "application/pdf")}).status_code == 201

    hits = asyncio.run(rag.retrieve("How much thrust does the Orion engine make?"))
    assert hits, "expected the PDF chunk to be retrieved"
    assert hits[0].source == "engine.pdf"
    assert hits[0].page == 2
    assert hits[0].label == "engine.pdf (p. 2)"


def test_docx_extraction(clean_index):
    data = _make_docx(["Quarterly revenue grew to 4.2 million euros.", "Headcount reached 58."])
    res = client.post(
        "/api/documents",
        files={"file": ("q3.docx", data, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    assert res.status_code == 201
    assert res.json()["chunks"] >= 1
