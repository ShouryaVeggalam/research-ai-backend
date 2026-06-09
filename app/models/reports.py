"""Research reports, executive briefs, and strategic recommendations."""
from __future__ import annotations

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.types import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin, UUIDMixin


class ResearchReport(UUIDMixin, TimestampMixin, Base):
    """A generated multi-agent research report."""

    __tablename__ = "research_reports"

    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    report_type: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    market_outlook: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    risk_outlook: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    opportunity_outlook: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    sections: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    generated_by: Mapped[str | None] = mapped_column(String(64), nullable=True)


class ExecutiveBrief(UUIDMixin, TimestampMixin, Base):
    """A CRO-authored executive brief."""

    __tablename__ = "executive_briefs"

    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    brief_type: Mapped[str] = mapped_column(String(32), index=True, nullable=False)

    executive_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    strategic_priorities: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    top_opportunities: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    top_risks: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    recommendations: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    strategic_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)


class Recommendation(UUIDMixin, TimestampMixin, Base):
    """A strategic recommendation from the Strategy or CRO agent."""

    __tablename__ = "recommendations"

    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)

    priority: Mapped[str | None] = mapped_column(String(32), index=True, nullable=True)
    priority_rank: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    action_plan: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    rationale: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    source_agent: Mapped[str | None] = mapped_column(String(64), nullable=True)
