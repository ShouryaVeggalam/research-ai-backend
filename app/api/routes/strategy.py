"""Strategy Agent & Chief Research Officer (CRO) orchestration endpoints."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.api.deps import CompanyId, CurrentUser, RequireAnalyst, DbSession
from app.schemas.reports import RecommendationRead
from app.services.intelligence_service import IntelligenceService
from app.services.orchestration_service import OrchestrationService
from app.repositories.reports import RecommendationRepository

strategy_router = APIRouter(prefix="/strategy", tags=["strategy"])
cro_router = APIRouter(prefix="/cro", tags=["cro"])


@strategy_router.post("/generate")
def generate_strategy(db: DbSession, company_id: CompanyId, _: RequireAnalyst) -> dict[str, Any]:
    """Run the Strategy Agent (over the full upstream pipeline)."""
    OrchestrationService(db).run_full_pipeline(company_id, persist=True)
    return IntelligenceService(db).run_agent(company_id, "strategy").as_dict()


@strategy_router.get("/recommendations", response_model=list[RecommendationRead])
def recommendations(db: DbSession, company_id: CompanyId, _: CurrentUser):
    items = RecommendationRepository(db).top(company_id, limit=50)
    return [RecommendationRead.model_validate(i) for i in items]


@cro_router.post("/run")
def run_cro(db: DbSession, company_id: CompanyId, _: RequireAnalyst) -> dict[str, Any]:
    """Run the full agent network orchestrated by the CRO."""
    results = OrchestrationService(db).run_full_pipeline(company_id, persist=True)
    return results.get("cro", {})


@cro_router.get("/summary")
def cro_summary(db: DbSession, company_id: CompanyId, _: CurrentUser) -> dict[str, Any]:
    """Run the CRO synthesis over current intelligence without re-persisting."""
    results = OrchestrationService(db).run_full_pipeline(company_id, persist=False)
    return results.get("cro", {})
