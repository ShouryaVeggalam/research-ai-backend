"""Runs the agent pipeline and persists its outputs."""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.agents.base import AgentResult
from app.agents.orchestrator import run_pipeline, run_single
from app.core.constants import ReportType
from app.core.logging import get_logger
from app.repositories.intelligence import (
    CompetitorRepository,
    IndustryRepository,
    MarketRepository,
    OpportunityRepository,
    RiskRepository,
    TrendRepository,
)
from app.repositories.reports import ExecutiveBriefRepository, RecommendationRepository
from app.repositories.system import ActivityLogRepository
from app.services.context_builder import build_context

logger = get_logger("services.orchestration")


class OrchestrationService:
    def __init__(self, db: Session):
        self.db = db

    # ---- single agent ----
    def run_agent(self, company_id: str, agent_name: str) -> AgentResult:
        context = build_context(self.db, company_id)
        result = run_single(agent_name, context)
        ActivityLogRepository(self.db).create(
            company_id=company_id,
            action="agent.run",
            entity_type="agent",
            entity_id=agent_name,
            detail={"score": result.score, "confidence": result.confidence},
        )
        self.db.commit()
        return result

    # ---- full pipeline ----
    def run_full_pipeline(self, company_id: str, *, persist: bool = True) -> dict[str, Any]:
        context = build_context(self.db, company_id)
        results = run_pipeline(context)
        if persist:
            self._persist(company_id, results)
        ActivityLogRepository(self.db).create(
            company_id=company_id,
            action="pipeline.run",
            entity_type="pipeline",
            detail={"agents": list(results.keys())},
        )
        self.db.commit()
        return results

    # ---- persistence of derived intelligence ----
    def _persist(self, company_id: str, results: dict[str, Any]) -> None:
        self._update_scores(company_id, results)
        self._persist_opportunities(company_id, results.get("opportunity", {}))
        self._persist_risks(company_id, results.get("risk", {}))
        self._persist_recommendations(company_id, results.get("strategy", {}))
        self._persist_brief(company_id, results.get("cro", {}))

    def _update_scores(self, company_id: str, results: dict[str, Any]) -> None:
        # Markets
        market_repo = MarketRepository(self.db)
        for f in results.get("market", {}).get("findings", []):
            if f.get("market_id"):
                obj = market_repo.get(f["market_id"])
                if obj:
                    market_repo.update(
                        obj,
                        market_score=f.get("market_score"),
                        attractiveness=f.get("attractiveness"),
                        segmentation=f.get("segmentation"),
                    )
        # Competitors
        comp_repo = CompetitorRepository(self.db)
        for f in results.get("competitor", {}).get("findings", []):
            if f.get("competitor_id"):
                obj = comp_repo.get(f["competitor_id"])
                if obj:
                    comp_repo.update(
                        obj,
                        competitor_score=f.get("competitor_score"),
                        threat_level=f.get("threat_level"),
                        updates=f.get("updates"),
                    )
        # Industries
        ind_repo = IndustryRepository(self.db)
        for f in results.get("industry", {}).get("findings", []):
            if f.get("industry_id"):
                obj = ind_repo.get(f["industry_id"])
                if obj:
                    ind_repo.update(
                        obj, industry_score=f.get("industry_score"), health=f.get("health")
                    )
        # Trends (tracked)
        trend_repo = TrendRepository(self.db)
        for f in results.get("trend", {}).get("findings", []):
            if f.get("source") == "tracked" and f.get("name"):
                obj = trend_repo.get_by(company_id=company_id, name=f["name"])
                if obj:
                    trend_repo.update(
                        obj,
                        trend_score=f.get("trend_score"),
                        strength=f.get("strength"),
                        velocity=f.get("velocity"),
                        confidence=f.get("confidence"),
                    )

    def _persist_opportunities(self, company_id: str, out: dict[str, Any]) -> None:
        repo = OpportunityRepository(self.db)
        for f in out.get("findings", []):
            existing = repo.get_by(company_id=company_id, title=f.get("title"))
            payload = dict(
                opportunity_score=f.get("opportunity_score"),
                market_size_usd=f.get("market_size_usd"),
                revenue_potential_usd=f.get("revenue_potential_usd"),
                competition_score=f.get("competition_score"),
                growth_potential=f.get("growth_potential"),
                priority=f.get("priority"),
                category=f.get("category"),
                rationale=f.get("rationale"),
            )
            if existing:
                repo.update(existing, **payload)
            else:
                repo.create(company_id=company_id, title=f.get("title"), **payload)

    def _persist_risks(self, company_id: str, out: dict[str, Any]) -> None:
        repo = RiskRepository(self.db)
        for f in out.get("findings", []):
            if f.get("source") == "tracked":
                continue
            existing = repo.get_by(company_id=company_id, title=f.get("title"))
            payload = dict(
                category=f.get("category"),
                risk_score=f.get("risk_score"),
                likelihood=f.get("likelihood"),
                impact=f.get("impact"),
                severity=f.get("severity"),
            )
            if existing:
                repo.update(existing, **payload)
            else:
                repo.create(company_id=company_id, title=f.get("title"), **payload)

    def _persist_recommendations(self, company_id: str, out: dict[str, Any]) -> None:
        repo = RecommendationRepository(self.db)
        for f in out.get("findings", []):
            existing = repo.get_by(company_id=company_id, title=f.get("title"))
            payload = dict(
                category=f.get("category"),
                priority=f.get("priority"),
                priority_rank=f.get("priority_rank"),
                confidence=f.get("confidence"),
                action_plan={"steps": f.get("action_plan", [])},
                rationale=f.get("rationale"),
                source_agent="strategy",
            )
            if existing:
                repo.update(existing, **payload)
            else:
                repo.create(company_id=company_id, title=f.get("title"), **payload)

    def _persist_brief(self, company_id: str, out: dict[str, Any]) -> None:
        if not out:
            return
        metrics = out.get("metrics", {})
        ExecutiveBriefRepository(self.db).create(
            company_id=company_id,
            title="CRO Executive Brief",
            brief_type=ReportType.AD_HOC.value,
            executive_summary=out.get("summary"),
            strategic_priorities={"items": metrics.get("strategic_priorities", [])},
            top_opportunities={"items": metrics.get("top_opportunities", [])},
            top_risks={"items": metrics.get("top_risks", [])},
            recommendations={"items": metrics.get("executive_recommendations", [])},
            strategic_confidence=metrics.get("strategic_confidence"),
        )
