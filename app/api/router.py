"""Aggregates all versioned API routers."""
from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import auth, dashboard, engines, feed, reports, signals, strategy, system
from app.api.routes.intelligence import (
    competitor_router,
    customer_router,
    industry_router,
    market_router,
    opportunity_router,
    risk_router,
    trend_router,
)

api_router = APIRouter()

# Auth
api_router.include_router(auth.router)

# Intelligence agents (CRUD + /analyze)
api_router.include_router(market_router)
api_router.include_router(competitor_router)
api_router.include_router(customer_router)
api_router.include_router(trend_router)
api_router.include_router(industry_router)
api_router.include_router(opportunity_router)
api_router.include_router(risk_router)

# Strategy + CRO orchestration
api_router.include_router(strategy.strategy_router)
api_router.include_router(strategy.cro_router)

# Signal ingestion + live feed
api_router.include_router(signals.router)
api_router.include_router(feed.router)

# Engines
api_router.include_router(engines.opportunities_router)
api_router.include_router(engines.risk_engine_router)

# Reports / briefs
api_router.include_router(reports.router)

# Dashboard + search
api_router.include_router(dashboard.dashboard_router)
api_router.include_router(dashboard.search_router)

# Alerts + notifications
api_router.include_router(system.alerts_router)
api_router.include_router(system.notifications_router)
