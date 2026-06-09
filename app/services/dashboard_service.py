"""Dashboard aggregation service."""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.repositories.intelligence import (
    CompetitorRepository,
    IndustryRepository,
    MarketRepository,
    OpportunityRepository,
    RiskRepository,
    TrendRepository,
)
from app.repositories.reports import ExecutiveBriefRepository, RecommendationRepository
from app.repositories.signals import IntelligenceFeedRepository
from app.repositories.system import AlertRepository
from app.schemas.dashboard import DashboardResponse, DashboardStats
from app.utils.scoring import clamp


def _o(obj: Any, *fields: str) -> dict[str, Any]:
    return {f: getattr(obj, f, None) for f in fields}


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def build(self, company_id: str) -> DashboardResponse:
        markets = MarketRepository(self.db)
        competitors = CompetitorRepository(self.db)
        industries = IndustryRepository(self.db)
        opportunities = OpportunityRepository(self.db)
        trends = TrendRepository(self.db)
        risks = RiskRepository(self.db)
        alerts = AlertRepository(self.db)
        feed = IntelligenceFeedRepository(self.db)
        recs = RecommendationRepository(self.db)
        briefs = ExecutiveBriefRepository(self.db)

        stats = DashboardStats(
            markets_tracked=markets.count(company_id=company_id),
            competitors_tracked=competitors.count(company_id=company_id),
            industries_monitored=industries.count(company_id=company_id),
            opportunities_found=opportunities.count(company_id=company_id),
            trend_signals=trends.count(company_id=company_id),
            risk_alerts=len(alerts.open_alerts(company_id)),
        )

        top_opps = opportunities.top_opportunities(company_id, limit=5)
        top_risks = risks.top_risks(company_id, limit=5)
        feed_items = feed.latest(company_id, limit=10)
        recommendations = recs.top(company_id, limit=5)

        # research health = blend of coverage & confidence from latest brief
        latest_brief = briefs.list(company_id=company_id, limit=1)
        strategic_confidence = 0.0
        if latest_brief and latest_brief[0].strategic_confidence is not None:
            strategic_confidence = latest_brief[0].strategic_confidence

        coverage_components = [
            stats.markets_tracked,
            stats.competitors_tracked,
            stats.industries_monitored,
            stats.opportunities_found,
            stats.trend_signals,
        ]
        coverage = clamp(sum(1 for c in coverage_components if c > 0) / 5 * 100)
        research_health = round(clamp(0.6 * coverage + 0.4 * strategic_confidence * 100), 2)

        return DashboardResponse(
            stats=stats,
            research_health_score=research_health,
            strategic_confidence=round(strategic_confidence, 2),
            top_opportunities=[
                _o(o, "id", "title", "opportunity_score", "priority", "revenue_potential_usd")
                for o in top_opps
            ],
            top_risks=[
                _o(r, "id", "title", "category", "risk_score", "severity") for r in top_risks
            ],
            live_feed=[
                _o(f, "id", "title", "feed_type", "priority", "impact_score", "created_at")
                for f in feed_items
            ],
            executive_recommendations=[
                _o(r, "id", "title", "priority", "priority_rank", "category")
                for r in recommendations
            ],
        )
