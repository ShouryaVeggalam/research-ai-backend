"""Integration tests for the HTTP API."""
from __future__ import annotations


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_register_login_me(client):
    import uuid

    email = f"flow-{uuid.uuid4().hex[:8]}@celestra.ai"
    r = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123", "role": "analyst"},
    )
    assert r.status_code == 201, r.text

    r = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    assert r.status_code == 200
    tokens = r.json()
    assert "access_token" in tokens and "refresh_token" in tokens

    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    r = client.get("/api/v1/auth/me", headers=headers)
    assert r.status_code == 200
    assert r.json()["email"] == email

    r = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert r.status_code == 200


def test_requires_auth(client):
    assert client.get("/api/v1/dashboard").status_code == 401


def test_market_crud_and_analyze(client, auth_headers):
    r = client.post(
        "/api/v1/market",
        headers=auth_headers,
        json={"name": "Cloud AI", "region": "NA", "market_size_usd": 5_000_000_000, "growth_rate": 0.25},
    )
    assert r.status_code == 201, r.text
    market_id = r.json()["id"]

    r = client.get(f"/api/v1/market/{market_id}", headers=auth_headers)
    assert r.status_code == 200

    r = client.post("/api/v1/market/analyze", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["metrics"]["markets_analyzed"] >= 1


def test_signal_ingestion_and_feed(client, auth_headers):
    r = client.post(
        "/api/v1/signals/ingest",
        headers=auth_headers,
        json={
            "title": "Competitor raises huge funding round",
            "content": "A major rival announced record funding and strong growth.",
            "signal_type": "funding",
            "source": "news",
            "confidence": 0.9,
        },
    )
    assert r.status_code == 201, r.text
    assert r.json()["impact_score"] > 0

    r = client.get("/api/v1/feed", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["total"] >= 1


def test_full_pipeline_and_dashboard(client, auth_headers):
    client.post(
        "/api/v1/competitor",
        headers=auth_headers,
        json={"name": "Rival Inc", "funding_usd": 50_000_000, "employee_count": 300},
    )
    r = client.post("/api/v1/cro/run", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert "metrics" in r.json()

    r = client.get("/api/v1/dashboard", headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert "stats" in body
    assert "research_health_score" in body


def test_search(client, auth_headers):
    client.post(
        "/api/v1/market",
        headers=auth_headers,
        json={"name": "Quantum Computing Market", "region": "EU"},
    )
    r = client.get("/api/v1/search", headers=auth_headers, params={"q": "quantum"})
    assert r.status_code == 200
    assert r.json()["total"] >= 1
