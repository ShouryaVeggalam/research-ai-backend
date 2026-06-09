"""Opportunity Engine — generates and ranks growth opportunities."""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.agents.orchestrator import run_single
from app.repositories.intelligence import OpportunityRepository
from app.services.context_builder import build_context


class OpportunityEngine:
    """Produces opportunity scores, market size, competition level,
    revenue/growth potential and a priority ranking."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = OpportunityRepository(db)

    def generate(self, company_id: str, *, persist: bool = True) -> list[dict[str, Any]]:
        context = build_context(self.db, company_id)
        # Opportunity agent depends on upstream agents; run the chain it needs.
        for upstream in ("market", "competitor", "customer", "trend"):
            run_single(upstream, context)
        result = run_single("opportunity", context)
        findings = result.findings

        if persist:
            for f in findings:
                existing = self.repo.get_by(company_id=company_id, title=f.get("title"))
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
                    self.repo.update(existing, **payload)
                else:
                    self.repo.create(company_id=company_id, title=f.get("title"), **payload)
            self.db.commit()
        return findings

    def ranked(self, company_id: str, *, limit: int = 20) -> list:
        return self.repo.top_opportunities(company_id, limit=limit)
