"""Executive Brief Engine & Research Report generation."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.core.constants import ReportType
from app.models.reports import ExecutiveBrief, ResearchReport
from app.repositories.reports import ExecutiveBriefRepository, ResearchReportRepository
from app.services.orchestration_service import OrchestrationService


class ReportService:
    def __init__(self, db: Session):
        self.db = db
        self.reports = ResearchReportRepository(db)
        self.briefs = ExecutiveBriefRepository(db)

    def generate_brief(self, company_id: str, report_type: ReportType) -> ExecutiveBrief:
        results = OrchestrationService(self.db).run_full_pipeline(company_id, persist=True)
        cro = results.get("cro", {})
        metrics = cro.get("metrics", {})
        label = report_type.value.capitalize()
        brief = self.briefs.create(
            company_id=company_id,
            title=f"{label} Executive Brief — {datetime.now(timezone.utc).date()}",
            brief_type=report_type.value,
            executive_summary=cro.get("summary"),
            strategic_priorities={"items": metrics.get("strategic_priorities", [])},
            top_opportunities={"items": metrics.get("top_opportunities", [])},
            top_risks={"items": metrics.get("top_risks", [])},
            recommendations={"items": metrics.get("executive_recommendations", [])},
            strategic_confidence=metrics.get("strategic_confidence"),
        )
        self.db.commit()
        self.db.refresh(brief)
        return brief

    def generate_research_report(self, company_id: str, report_type: ReportType) -> ResearchReport:
        results = OrchestrationService(self.db).run_full_pipeline(company_id, persist=True)
        cro = results.get("cro", {})
        market = results.get("market", {})
        risk = results.get("risk", {})
        opportunity = results.get("opportunity", {})
        label = report_type.value.capitalize()

        sections = {
            name: {"summary": out.get("summary"), "score": out.get("score")}
            for name, out in results.items()
        }

        report = self.reports.create(
            company_id=company_id,
            title=f"{label} Research Report — {datetime.now(timezone.utc).date()}",
            report_type=report_type.value,
            summary=cro.get("summary"),
            market_outlook={
                "score": market.get("score"),
                "summary": market.get("summary"),
                "metrics": market.get("metrics"),
            },
            risk_outlook={
                "score": risk.get("score"),
                "summary": risk.get("summary"),
                "heatmap": risk.get("metrics", {}).get("risk_heatmap"),
            },
            opportunity_outlook={
                "top": opportunity.get("findings", [])[:5],
                "summary": opportunity.get("summary"),
            },
            sections=sections,
            confidence=cro.get("confidence"),
            generated_by="cro",
        )
        self.db.commit()
        self.db.refresh(report)
        return report

    def list_briefs(self, company_id: str, *, offset: int = 0, limit: int = 50):
        items = self.briefs.list(company_id=company_id, offset=offset, limit=limit)
        total = self.briefs.count(company_id=company_id)
        return items, total

    def list_reports(self, company_id: str, *, offset: int = 0, limit: int = 50):
        items = self.reports.list(company_id=company_id, offset=offset, limit=limit)
        total = self.reports.count(company_id=company_id)
        return items, total
