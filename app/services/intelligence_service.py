"""CRUD + agent-run service for core intelligence entities."""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.agents.base import AgentResult
from app.core.exceptions import NotFoundError
from app.repositories.intelligence import (
    CompetitorRepository,
    CustomerSegmentRepository,
    IndustryRepository,
    MarketRepository,
    OpportunityRepository,
    RiskRepository,
    TrendRepository,
)
from app.services.orchestration_service import OrchestrationService

_REPOS = {
    "market": MarketRepository,
    "competitor": CompetitorRepository,
    "customer": CustomerSegmentRepository,
    "trend": TrendRepository,
    "industry": IndustryRepository,
    "opportunity": OpportunityRepository,
    "risk": RiskRepository,
}


class IntelligenceService:
    """Generic CRUD for tenant-scoped intelligence entities + agent runs."""

    def __init__(self, db: Session):
        self.db = db

    def _repo(self, kind: str):
        return _REPOS[kind](self.db)

    def create(self, kind: str, company_id: str, data: dict[str, Any]):
        obj = self._repo(kind).create(company_id=company_id, **data)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get(self, kind: str, company_id: str, obj_id: str):
        obj = self._repo(kind).get(obj_id)
        if not obj or obj.company_id != company_id:
            raise NotFoundError(f"{kind} not found.")
        return obj

    def list(self, kind: str, company_id: str, *, offset: int = 0, limit: int = 50):
        repo = self._repo(kind)
        items = repo.list(company_id=company_id, offset=offset, limit=limit)
        total = repo.count(company_id=company_id)
        return items, total

    def update(self, kind: str, company_id: str, obj_id: str, data: dict[str, Any]):
        obj = self.get(kind, company_id, obj_id)
        updated = self._repo(kind).update(obj, **data)
        self.db.commit()
        self.db.refresh(updated)
        return updated

    def delete(self, kind: str, company_id: str, obj_id: str) -> None:
        obj = self.get(kind, company_id, obj_id)
        self._repo(kind).delete(obj)
        self.db.commit()

    def run_agent(self, company_id: str, agent_name: str) -> AgentResult:
        return OrchestrationService(self.db).run_agent(company_id, agent_name)
