"""Repositories for core intelligence entities."""
from __future__ import annotations

from app.models.intelligence import (
    Competitor,
    CustomerSegment,
    Industry,
    Market,
    Opportunity,
    Risk,
    Trend,
)
from app.repositories.base import BaseRepository


class MarketRepository(BaseRepository[Market]):
    model = Market

    def top_attractive(self, company_id: str, limit: int = 5) -> list[Market]:
        return self.list(
            company_id=company_id,
            limit=limit,
            order_by=Market.attractiveness.desc().nullslast(),
        )


class CompetitorRepository(BaseRepository[Competitor]):
    model = Competitor

    def top_threats(self, company_id: str, limit: int = 5) -> list[Competitor]:
        return self.list(
            company_id=company_id,
            limit=limit,
            order_by=Competitor.competitor_score.desc().nullslast(),
        )


class CustomerSegmentRepository(BaseRepository[CustomerSegment]):
    model = CustomerSegment


class TrendRepository(BaseRepository[Trend]):
    model = Trend

    def top_trends(self, company_id: str, limit: int = 5) -> list[Trend]:
        return self.list(
            company_id=company_id,
            limit=limit,
            order_by=Trend.trend_score.desc().nullslast(),
        )


class IndustryRepository(BaseRepository[Industry]):
    model = Industry


class OpportunityRepository(BaseRepository[Opportunity]):
    model = Opportunity

    def top_opportunities(self, company_id: str, limit: int = 5) -> list[Opportunity]:
        return self.list(
            company_id=company_id,
            limit=limit,
            order_by=Opportunity.opportunity_score.desc().nullslast(),
        )


class RiskRepository(BaseRepository[Risk]):
    model = Risk

    def top_risks(self, company_id: str, limit: int = 5) -> list[Risk]:
        return self.list(
            company_id=company_id,
            limit=limit,
            order_by=Risk.risk_score.desc().nullslast(),
        )
