# Celestra Research AI — Backend

**Your AI Strategy Department.**

Celestra Research AI is a production-grade **strategic intelligence platform**.
It is *not* a search engine, *not* a chatbot, and *not* a report database — it
is a system that continuously **collects, analyzes, and synthesizes** strategic
intelligence through a network of specialized AI agents orchestrated by a
**Chief Research Officer (CRO)** agent.

---

## Architecture

```
Signals
   ↓
Market Intelligence Agent
   ↓
Competitor Intelligence Agent
   ↓
Customer Intelligence Agent
   ↓
Trend Intelligence Agent
   ↓
Industry Intelligence Agent
   ↓
Opportunity Discovery Agent
   ↓
Risk Intelligence Agent
   ↓
Strategy Agent
   ↓
Chief Research Officer Agent  →  Executive Brief
```

The pipeline is orchestrated with **LangGraph** (with a deterministic sequential
fallback). Every agent ships with explainable, deterministic heuristics so the
platform is **fully functional without any LLM**. When `LLM_ENABLED=true` and an
`OPENAI_API_KEY` is configured, agents use an **OpenAI-compatible** model
(via LangChain) to enrich narrative summaries.

### Tech stack

Python 3.12 · FastAPI · PostgreSQL · SQLAlchemy 2.0 · Alembic · Redis · Celery ·
Pydantic v2 · JWT auth · Docker · OpenAPI · LangGraph · LangChain · WebSockets.

---

## Project layout

```
backend/
  app/
    agents/        # 9 agents (market…cro) + orchestrator + registry
    api/           # FastAPI routers, deps (auth/RBAC/tenancy)
    core/          # config, logging, security, exceptions, constants
    database/      # engine, session, declarative base
    models/        # 17 SQLAlchemy models
    repositories/  # repository pattern (data access)
    schemas/       # Pydantic request/response models
    services/      # business logic + engines (signal/opportunity/risk/report…)
    utils/         # deterministic scoring & text heuristics
    workers/       # Celery app + scheduled jobs
    bootstrap.py   # schema creation + admin seed
    main.py        # application factory
  alembic/         # migrations
  tests/           # unit + integration tests
```

---

## Quick start (Docker)

```bash
cd backend
cp .env.example .env
docker compose up --build
```

This starts Postgres, Redis, the API (`:8000`), a Celery worker, and Celery beat.
Open the interactive docs at **http://localhost:8000/docs**.

A bootstrap admin is created on first start (see `.env`):
`admin@celestra.ai` / `admin12345`.

## Quick start (local)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# Option A: let the app create tables on startup (dev)
uvicorn app.main:app --reload

# Option B: run migrations explicitly
alembic upgrade head
```

Run background workers locally:

```bash
celery -A app.workers.celery_app.celery_app worker --loglevel=info
celery -A app.workers.celery_app.celery_app beat   --loglevel=info
```

---

## Authentication & roles

JWT access + refresh tokens. Role-based access control with hierarchy:

`viewer < analyst < research_manager < founder < admin`

| Action                              | Minimum role      |
|-------------------------------------|-------------------|
| Read intelligence, dashboard, feed  | viewer            |
| Create/update entities, run agents  | analyst           |
| Delete entities, generate reports   | research_manager  |

```bash
# Login
curl -X POST localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@celestra.ai","password":"admin12345"}'
```

---

## Key endpoints

| Area              | Method & path |
|-------------------|---------------|
| Auth              | `POST /api/v1/auth/{register,login,refresh}`, `GET /auth/me` |
| Market agent      | `… /api/v1/market` (CRUD) · `POST /market/analyze` |
| Competitor agent  | `… /api/v1/competitor` · `POST /competitor/analyze` |
| Customer agent    | `… /api/v1/customer` · `POST /customer/analyze` |
| Trend agent       | `… /api/v1/trend` · `POST /trend/analyze` |
| Industry agent    | `… /api/v1/industry` · `POST /industry/analyze` |
| Opportunity agent | `… /api/v1/opportunity` · `POST /opportunity/analyze` |
| Risk agent        | `… /api/v1/risk` · `POST /risk/analyze` |
| Strategy          | `POST /api/v1/strategy/generate` · `GET /strategy/recommendations` |
| CRO orchestration | `POST /api/v1/cro/run` · `GET /cro/summary` |
| Signal ingestion  | `POST /api/v1/signals/ingest`, `/signals/ingest/batch` |
| Live feed         | `GET /api/v1/feed` · WebSocket `…/feed/ws?token=<JWT>` |
| Opportunity engine| `POST /api/v1/opportunities/generate` · `GET /opportunities` |
| Risk engine       | `POST /api/v1/risk-engine/compute` · `GET /risk-engine/heatmap` |
| Reports           | `POST /api/v1/reports/{brief,research}` · `GET /reports`, `/reports/briefs` |
| Dashboard         | `GET /api/v1/dashboard` |
| Global search     | `GET /api/v1/search?q=…` |
| Alerts / notifs   | `GET /api/v1/alerts`, `/notifications` |

---

## Background jobs (Celery beat)

| Schedule | Task |
|----------|------|
| Hourly   | signal / trend / competitor / opportunity / risk refresh |
| Daily 06:00 UTC | executive brief |
| Weekly Mon 07:00 UTC | research report |
| Monthly 1st 08:00 UTC | strategic outlook report |

---

## Testing

```bash
cd backend
pip install -r requirements.txt
pytest -q
```

Tests use an isolated SQLite database and run with no external services.

---

## Configuration

All configuration is environment-driven (see `.env.example`). Notable flags:

- `LLM_ENABLED` / `OPENAI_API_KEY` — enable LLM narrative enrichment.
- `APP_ENV` — when not `production`, tables are auto-created on startup.
- `DATABASE_URL` — full override for the SQLAlchemy URL.
