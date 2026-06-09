"""Factory building CRUD + agent-run routers for intelligence entities.

Produces the per-agent endpoints required by the spec:
``/market``, ``/competitor``, ``/customer``, ``/trend``, ``/industry``,
``/opportunity`` and ``/risk`` — each with full CRUD plus ``/analyze`` which
runs the corresponding intelligence agent.

NOTE: this module intentionally does **not** use ``from __future__ import
annotations``. The CRUD routers are generated dynamically and bind the request
schema as a *closure variable* used directly as a parameter annotation. Under
PEP 563 (stringized annotations) FastAPI cannot resolve those local names, so we
keep real annotation objects here.
"""
from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.api.deps import CompanyId, CurrentUser, RequireAnalyst, RequireManager
from app.api.deps import DbSession
from app.schemas.common import PaginatedResponse
from app.schemas.intelligence import (
    CompetitorCreate,
    CompetitorRead,
    CompetitorUpdate,
    CustomerSegmentCreate,
    CustomerSegmentRead,
    IndustryCreate,
    IndustryRead,
    MarketCreate,
    MarketRead,
    MarketUpdate,
    OpportunityCreate,
    OpportunityRead,
    RiskCreate,
    RiskRead,
    TrendCreate,
    TrendRead,
)
from app.services.intelligence_service import IntelligenceService


def build_router(
    *,
    kind: str,
    agent_name: str,
    prefix: str,
    tag: str,
    create_schema: type[BaseModel],
    read_schema: type[BaseModel],
    update_schema: type[BaseModel] | None = None,
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=[tag])

    @router.post("", response_model=read_schema, status_code=201)
    def create(payload: create_schema, db: DbSession, company_id: CompanyId, _: RequireAnalyst):  # type: ignore[valid-type]
        obj = IntelligenceService(db).create(kind, company_id, payload.model_dump(exclude_unset=True))
        return read_schema.model_validate(obj)

    @router.get("", response_model=PaginatedResponse[read_schema])
    def list_items(
        db: DbSession,
        company_id: CompanyId,
        _: CurrentUser,
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1, le=200),
    ):
        items, total = IntelligenceService(db).list(
            kind, company_id, offset=(page - 1) * size, limit=size
        )
        return PaginatedResponse[read_schema](
            items=[read_schema.model_validate(i) for i in items],
            total=total,
            page=page,
            size=size,
        )

    @router.post("/analyze")
    def analyze(db: DbSession, company_id: CompanyId, _: RequireAnalyst) -> dict[str, Any]:
        result = IntelligenceService(db).run_agent(company_id, agent_name)
        return result.as_dict()

    @router.get("/{item_id}", response_model=read_schema)
    def get_item(item_id: str, db: DbSession, company_id: CompanyId, _: CurrentUser):
        obj = IntelligenceService(db).get(kind, company_id, item_id)
        return read_schema.model_validate(obj)

    if update_schema is not None:

        @router.patch("/{item_id}", response_model=read_schema)
        def update_item(
            item_id: str,
            payload: update_schema,  # type: ignore[valid-type]
            db: DbSession,
            company_id: CompanyId,
            _: RequireAnalyst,
        ):
            obj = IntelligenceService(db).update(
                kind, company_id, item_id, payload.model_dump(exclude_unset=True)
            )
            return read_schema.model_validate(obj)

    @router.delete("/{item_id}", status_code=204)
    def delete_item(item_id: str, db: DbSession, company_id: CompanyId, _: RequireManager):
        IntelligenceService(db).delete(kind, company_id, item_id)

    return router


market_router = build_router(
    kind="market", agent_name="market", prefix="/market", tag="market",
    create_schema=MarketCreate, read_schema=MarketRead, update_schema=MarketUpdate,
)
competitor_router = build_router(
    kind="competitor", agent_name="competitor", prefix="/competitor", tag="competitor",
    create_schema=CompetitorCreate, read_schema=CompetitorRead, update_schema=CompetitorUpdate,
)
customer_router = build_router(
    kind="customer", agent_name="customer", prefix="/customer", tag="customer",
    create_schema=CustomerSegmentCreate, read_schema=CustomerSegmentRead,
)
trend_router = build_router(
    kind="trend", agent_name="trend", prefix="/trend", tag="trend",
    create_schema=TrendCreate, read_schema=TrendRead,
)
industry_router = build_router(
    kind="industry", agent_name="industry", prefix="/industry", tag="industry",
    create_schema=IndustryCreate, read_schema=IndustryRead,
)
opportunity_router = build_router(
    kind="opportunity", agent_name="opportunity", prefix="/opportunity", tag="opportunity",
    create_schema=OpportunityCreate, read_schema=OpportunityRead,
)
risk_router = build_router(
    kind="risk", agent_name="risk", prefix="/risk", tag="risk",
    create_schema=RiskCreate, read_schema=RiskRead,
)
