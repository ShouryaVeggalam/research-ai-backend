"""Builds an :class:`AgentContext` from persisted company data."""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.agents.base import AgentContext
from app.models.intelligence import (
    Competitor,
    CustomerSegment,
    Industry,
    Market,
    Opportunity,
    Risk,
    Trend,
)
from app.models.signals import Signal
from app.repositories.intelligence import (
    CompetitorRepository,
    CustomerSegmentRepository,
    IndustryRepository,
    MarketRepository,
    OpportunityRepository,
    RiskRepository,
    TrendRepository,
)
from app.repositories.signals import SignalRepository
from app.repositories.user import CompanyRepository


def _row_to_dict(obj: Any) -> dict[str, Any]:
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def build_context(
    db: Session,
    company_id: str,
    *,
    signal_limit: int = 200,
    params: dict[str, Any] | None = None,
) -> AgentContext:
    """Assemble all the data an agent pipeline needs for ``company_id``."""
    company = CompanyRepository(db).get(company_id)
    company_name = company.name if company else "Company"

    signals = SignalRepository(db).list(
        company_id=company_id, limit=signal_limit, order_by=Signal.occurred_at.desc()
    )

    entities = {
        "markets": [_row_to_dict(m) for m in MarketRepository(db).list(company_id=company_id, limit=200)],
        "competitors": [
            _row_to_dict(c) for c in CompetitorRepository(db).list(company_id=company_id, limit=200)
        ],
        "customer_segments": [
            _row_to_dict(c)
            for c in CustomerSegmentRepository(db).list(company_id=company_id, limit=200)
        ],
        "trends": [_row_to_dict(t) for t in TrendRepository(db).list(company_id=company_id, limit=200)],
        "industries": [
            _row_to_dict(i) for i in IndustryRepository(db).list(company_id=company_id, limit=200)
        ],
        "opportunities": [
            _row_to_dict(o) for o in OpportunityRepository(db).list(company_id=company_id, limit=200)
        ],
        "risks": [_row_to_dict(r) for r in RiskRepository(db).list(company_id=company_id, limit=200)],
    }

    return AgentContext(
        company_id=company_id,
        company_name=company_name,
        signals=[_row_to_dict(s) for s in signals],
        entities=entities,
        params=params or {},
    )
