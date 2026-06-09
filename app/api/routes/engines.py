"""Opportunity Engine & Risk Engine endpoints."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from app.api.deps import CompanyId, CurrentUser, RequireAnalyst, DbSession
from app.schemas.intelligence import OpportunityRead
from app.services.opportunity_engine import OpportunityEngine
from app.services.risk_engine import RiskEngine

opportunities_router = APIRouter(prefix="/opportunities", tags=["opportunity-engine"])
risk_engine_router = APIRouter(prefix="/risk-engine", tags=["risk-engine"])


@opportunities_router.post("/generate")
def generate_opportunities(db: DbSession, company_id: CompanyId, _: RequireAnalyst) -> list[dict[str, Any]]:
    return OpportunityEngine(db).generate(company_id, persist=True)


@opportunities_router.get("", response_model=list[OpportunityRead])
def ranked_opportunities(
    db: DbSession,
    company_id: CompanyId,
    _: CurrentUser,
    limit: int = Query(20, ge=1, le=100),
):
    items = OpportunityEngine(db).ranked(company_id, limit=limit)
    return [OpportunityRead.model_validate(i) for i in items]


@risk_engine_router.post("/compute")
def compute_risk(db: DbSession, company_id: CompanyId, _: RequireAnalyst) -> dict[str, Any]:
    """Return the risk matrix, heatmap and aggregate score."""
    return RiskEngine(db).compute(company_id, persist=True)


@risk_engine_router.get("/heatmap")
def risk_heatmap(db: DbSession, company_id: CompanyId, _: CurrentUser) -> dict[str, Any]:
    return RiskEngine(db).compute(company_id, persist=False)
