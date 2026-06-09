"""Pytest fixtures. Uses an isolated SQLite database so tests need no services."""
from __future__ import annotations

import os

# Configure environment BEFORE importing the application.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_celestra.db")
os.environ.setdefault("LLM_ENABLED", "false")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("APP_ENV", "test")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import app.models  # noqa: F401,E402  register models
from app.database.base import Base  # noqa: E402
from app.database.session import engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers(client) -> dict:
    """Register a unique analyst-or-higher user and return auth headers."""
    import uuid

    email = f"user-{uuid.uuid4().hex[:8]}@celestra.ai"
    password = "supersecret"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Test", "role": "founder"},
    )
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
