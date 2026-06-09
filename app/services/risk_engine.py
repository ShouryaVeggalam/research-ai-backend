"""Risk Engine — computes risk matrix, heatmap and aggregate score."""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.agents.orchestrator import run_single
from app.core.constants import AlertStatus, Priority
from app.repositories.intelligence import RiskRepository
from app.repositories.system import AlertRepository
from app.services.context_builder import build_context
from app.utils.scoring import priority_from_score


class RiskEngine:
    """Calculates market, competitive, economic, technology & regulatory risk."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = RiskRepository(db)
        self.alerts = AlertRepository(db)

    def compute(self, company_id: str, *, persist: bool = True) -> dict[str, Any]:
        context = build_context(self.db, company_id)
        for upstream in ("market", "competitor"):
            run_single(upstream, context)
        result = run_single("risk", context)

        heatmap = result.metrics.get("risk_heatmap", {})
        matrix = result.metrics.get("risk_matrix", [])
        aggregate = result.score

        if persist:
            for f in result.findings:
                if f.get("source") == "tracked":
                    continue
                existing = self.repo.get_by(company_id=company_id, title=f.get("title"))
                payload = dict(
                    category=f.get("category"),
                    risk_score=f.get("risk_score"),
                    likelihood=f.get("likelihood"),
                    impact=f.get("impact"),
                    severity=f.get("severity"),
                )
                if existing:
                    self.repo.update(existing, **payload)
                else:
                    self.repo.create(company_id=company_id, title=f.get("title"), **payload)
                # raise alerts for severe risks
                if (f.get("risk_score") or 0) >= 60:
                    self._raise_alert(company_id, f)
            self.db.commit()

        return {
            "aggregate_risk_score": aggregate,
            "risk_heatmap": heatmap,
            "risk_matrix": matrix,
            "risks": result.findings,
        }

    def _raise_alert(self, company_id: str, finding: dict[str, Any]) -> None:
        existing = self.alerts.get_by(
            company_id=company_id, title=f"Risk: {finding.get('title')}", status=AlertStatus.OPEN.value
        )
        if existing:
            return
        priority = priority_from_score(finding.get("risk_score") or 0)
        self.alerts.create(
            company_id=company_id,
            title=f"Risk: {finding.get('title')}",
            message=f"{finding.get('category')} risk at {finding.get('severity')} severity.",
            alert_type="risk",
            priority=priority.value if isinstance(priority, Priority) else priority,
            severity_score=finding.get("risk_score"),
            context=finding,
        )
