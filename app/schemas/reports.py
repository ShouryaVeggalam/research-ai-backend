"""Report, brief & recommendation schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.core.constants import ReportType


class ReportRequest(BaseModel):
    report_type: ReportType = ReportType.WEEKLY
    title: str | None = None


class ResearchReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    title: str
    report_type: str
    summary: str | None
    market_outlook: dict[str, Any] | None
    risk_outlook: dict[str, Any] | None
    opportunity_outlook: dict[str, Any] | None
    sections: dict[str, Any] | None
    confidence: float | None
    generated_by: str | None
    created_at: datetime


class ExecutiveBriefRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    title: str
    brief_type: str
    executive_summary: str | None
    strategic_priorities: dict[str, Any] | None
    top_opportunities: dict[str, Any] | None
    top_risks: dict[str, Any] | None
    recommendations: dict[str, Any] | None
    strategic_confidence: float | None
    created_at: datetime


class RecommendationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    title: str
    description: str | None
    category: str | None
    priority: str | None
    priority_rank: float | None
    confidence: float | None
    action_plan: dict[str, Any] | None
    rationale: dict[str, Any] | None
    source_agent: str | None
    created_at: datetime
