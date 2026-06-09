"""Executive brief & research report endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Query

from app.api.deps import CompanyId, CurrentUser, RequireManager, DbSession
from app.schemas.reports import (
    ExecutiveBriefRead,
    ReportRequest,
    ResearchReportRead,
)
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/brief", response_model=ExecutiveBriefRead, status_code=201)
def generate_brief(payload: ReportRequest, db: DbSession, company_id: CompanyId, _: RequireManager):
    brief = ReportService(db).generate_brief(company_id, payload.report_type)
    return ExecutiveBriefRead.model_validate(brief)


@router.post("/research", response_model=ResearchReportRead, status_code=201)
def generate_report(payload: ReportRequest, db: DbSession, company_id: CompanyId, _: RequireManager):
    report = ReportService(db).generate_research_report(company_id, payload.report_type)
    return ResearchReportRead.model_validate(report)


@router.get("/briefs", response_model=list[ExecutiveBriefRead])
def list_briefs(
    db: DbSession,
    company_id: CompanyId,
    _: CurrentUser,
    limit: int = Query(20, ge=1, le=100),
):
    items, _total = ReportService(db).list_briefs(company_id, limit=limit)
    return [ExecutiveBriefRead.model_validate(i) for i in items]


@router.get("", response_model=list[ResearchReportRead])
def list_reports(
    db: DbSession,
    company_id: CompanyId,
    _: CurrentUser,
    limit: int = Query(20, ge=1, le=100),
):
    items, _total = ReportService(db).list_reports(company_id, limit=limit)
    return [ResearchReportRead.model_validate(i) for i in items]
