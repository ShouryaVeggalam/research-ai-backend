"""Celestra Research AI — FastAPI application factory."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.api.routes import health
from app.core.config import settings
from app.core.exceptions import CelestraError
from app.core.logging import configure_logging, get_logger

configure_logging()
logger = get_logger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("app.startup", env=settings.APP_ENV, llm_active=settings.llm_active)
    # Best-effort schema creation + admin seed (safe to skip if DB is absent).
    try:
        from app.bootstrap import run_bootstrap

        run_bootstrap(create_tables=settings.APP_ENV != "production")
    except Exception as exc:  # pragma: no cover - DB might be migrated separately
        logger.warning("app.bootstrap_skipped", error=str(exc))
    yield
    logger.info("app.shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description=(
            "Celestra Research AI — Your AI Strategy Department.\n\n"
            "A continuous strategic-intelligence platform powered by a network "
            "of specialized agents orchestrated by a Chief Research Officer."
        ),
        version="1.0.0",
        lifespan=lifespan,
        openapi_tags=[
            {"name": "auth", "description": "Authentication & JWT tokens"},
            {"name": "market", "description": "Market Intelligence Agent"},
            {"name": "competitor", "description": "Competitor Intelligence Agent"},
            {"name": "customer", "description": "Customer Intelligence Agent"},
            {"name": "trend", "description": "Trend Intelligence Agent"},
            {"name": "industry", "description": "Industry Intelligence Agent"},
            {"name": "opportunity", "description": "Opportunity Discovery Agent"},
            {"name": "risk", "description": "Risk Intelligence Agent"},
            {"name": "strategy", "description": "Strategy Agent"},
            {"name": "cro", "description": "Chief Research Officer orchestration"},
            {"name": "signals", "description": "Signal ingestion pipeline"},
            {"name": "feed", "description": "Live intelligence feed (REST + WebSocket)"},
            {"name": "dashboard", "description": "Aggregated dashboard"},
            {"name": "search", "description": "Global search"},
            {"name": "reports", "description": "Executive briefs & research reports"},
        ],
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(CelestraError)
    async def handle_celestra_error(request: Request, exc: CelestraError):
        logger.info("error.handled", code=exc.code, path=str(request.url.path))
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    app.include_router(health.router)
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    return app


app = create_app()
