from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/api/health").json() == {"status": "ok"}


def test_chat_llm_has_no_sources():
    res = client.post("/api/chat", json={"question": "hi", "mode": "llm"})
    assert res.status_code == 200
    assert res.json()["sources"] == []


def test_chat_rag_returns_sources():
    res = client.post("/api/chat", json={"question": "hi", "mode": "llm_rag"})
    assert res.status_code == 200
    assert res.json()["sources"]


def test_chat_rejects_empty_question():
    assert client.post("/api/chat", json={"question": "", "mode": "llm"}).status_code == 422
