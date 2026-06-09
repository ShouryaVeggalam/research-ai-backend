"""Dashboard aggregation & search schemas."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class DashboardStats(BaseModel):
    markets_tracked: int
    competitors_tracked: int
    industries_monitored: int
    opportunities_found: int
    trend_signals: int
    risk_alerts: int


class DashboardResponse(BaseModel):
    stats: DashboardStats
    research_health_score: float
    strategic_confidence: float
    top_opportunities: list[dict[str, Any]]
    top_risks: list[dict[str, Any]]
    live_feed: list[dict[str, Any]]
    executive_recommendations: list[dict[str, Any]]


class SearchHit(BaseModel):
    entity_type: str
    id: str
    title: str
    snippet: str | None = None
    score: float = 0.0


class SearchResponse(BaseModel):
    query: str
    total: int
    hits: list[SearchHit]
