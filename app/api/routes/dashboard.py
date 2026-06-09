"""Single-endpoint dashboard aggregation + global search."""
from __future__ import annotations

from fastapi import APIRouter, Query

from app.api.deps import CompanyId, CurrentUser, DbSession
from app.schemas.dashboard import DashboardResponse, SearchResponse
from app.services.dashboard_service import DashboardService
from app.services.search_service import SearchService

dashboard_router = APIRouter(prefix="/dashboard", tags=["dashboard"])
search_router = APIRouter(prefix="/search", tags=["search"])


@dashboard_router.get("", response_model=DashboardResponse)
def dashboard(db: DbSession, company_id: CompanyId, _: CurrentUser):
    return DashboardService(db).build(company_id)


@search_router.get("", response_model=SearchResponse)
def search(
    db: DbSession,
    company_id: CompanyId,
    _: CurrentUser,
    q: str = Query(..., min_length=1, description="Search query"),
):
    return SearchService(db).search(company_id, q)
