"""Shared test fixtures."""

import os
import pytest
from fastapi.testclient import TestClient

os.environ["OLLAMA_URL"] = "http://localhost:11434"
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ["JWT_SECRET"] = "test-secret-key-for-ci"

from backend.main import app, startup
from backend.config import EMBEDDINGS_PATH
from backend.db.store import init_db, get_conn
from backend.auth.security import init_auth_db


def _has_embeddings() -> bool:
    return os.path.isfile(EMBEDDINGS_PATH)


@pytest.fixture(scope="session", autouse=True)
def setup_app():
    """Initialize app — loads embeddings only when the file exists."""
    if _has_embeddings():
        startup()
    else:
        # CI environment: init DB only, skip embeddings
        init_db()
        init_auth_db()
    yield
    with get_conn() as conn:
        conn.execute("DELETE FROM messages")
        conn.execute("DELETE FROM conversations")
        conn.execute("DELETE FROM users")


requires_embeddings = pytest.mark.skipif(
    not _has_embeddings(),
    reason="embeddings.joblib not available (CI environment)",
)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    """Register a fresh test user and return auth headers."""
    username = f"testuser_{os.urandom(4).hex()}"
    res = client.post("/api/auth/register", json={
        "username": username,
        "password": "testpass123",
    })
    assert res.status_code == 200, f"Registration failed: {res.text}"
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_user(client):
    """Register a fresh user and return (headers, username)."""
    username = f"testuser_{os.urandom(4).hex()}"
    res = client.post("/api/auth/register", json={
        "username": username,
        "password": "testpass123",
    })
    assert res.status_code == 200
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return headers, username
