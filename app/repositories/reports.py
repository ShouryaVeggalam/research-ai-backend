"""Report, brief & recommendation repositories."""
from __future__ import annotations

from app.models.reports import ExecutiveBrief, Recommendation, ResearchReport
from app.repositories.base import BaseRepository


class ResearchReportRepository(BaseRepository[ResearchReport]):
    model = ResearchReport


class ExecutiveBriefRepository(BaseRepository[ExecutiveBrief]):
    model = ExecutiveBrief


class RecommendationRepository(BaseRepository[Recommendation]):
    model = Recommendation

    def top(self, company_id: str, limit: int = 5) -> list[Recommendation]:
        return self.list(
            company_id=company_id,
            limit=limit,
            order_by=Recommendation.priority_rank.asc().nullslast(),
        )
