import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import llm

client = TestClient(app)


@pytest.fixture
def fake_llm(monkeypatch):
    """Replace the network call so tests never hit DeepSeek."""
    calls = []

    async def _complete(messages):
        calls.append(messages)
        return "stub answer"

    monkeypatch.setattr(llm, "complete", _complete)
    return calls


def test_health():
    body = client.get("/api/health").json()
    assert body["status"] == "ok"
    assert "llm_configured" in body


def test_chat_llm_mode_skips_retrieval(fake_llm):
    res = client.post("/api/chat", json={"question": "hi", "mode": "llm"})
    assert res.status_code == 200
    assert res.json() == {"answer": "stub answer", "sources": []}
    assert "Context passages" not in fake_llm[0][1]["content"]


def test_chat_rag_mode_without_documents(clean_index, fake_llm):
    res = client.post("/api/chat", json={"question": "hi", "mode": "llm_rag"})
    assert res.status_code == 200
    assert "Upload documents first" in res.json()["answer"]
    assert fake_llm == []  # no LLM call when there is nothing to ground on


def test_chat_rag_mode_uses_retrieved_context(clean_index, fake_llm):
    upload = client.post(
        "/api/documents",
        files={"file": ("solar.txt", b"The Sahara Solar Plant produces 480 megawatts of power.", "text/plain")},
    )
    assert upload.status_code == 201

    res = client.post(
        "/api/chat", json={"question": "How much power does the Sahara plant produce?", "mode": "llm_rag"}
    )
    assert res.status_code == 200
    body = res.json()
    assert body["answer"] == "stub answer"
    assert body["sources"][0]["source"] == "solar.txt"
    assert "480 megawatts" in fake_llm[0][1]["content"]


def test_chat_reports_missing_api_key(monkeypatch):
    monkeypatch.setattr(llm.settings, "deepseek_api_key", "")
    res = client.post("/api/chat", json={"question": "hi", "mode": "llm"})
    assert res.status_code == 503
    assert "DEEPSEEK_API_KEY" in res.json()["detail"]


def test_chat_rejects_empty_question():
    assert client.post("/api/chat", json={"question": "", "mode": "llm"}).status_code == 422
