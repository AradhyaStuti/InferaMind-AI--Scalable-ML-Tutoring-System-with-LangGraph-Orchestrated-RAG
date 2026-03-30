"""Test health and general endpoints."""


def test_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["embedding_model"] == "bge-m3"
    assert data["llm_model"] == "llama3.2"


def test_chat_requires_auth(client):
    res = client.post("/api/chat", json={"message": "hello"})
    assert res.status_code == 401
