"""Core intelligence-domain models produced/consumed by agents."""
from __future__ import annotations

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.types import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin, UUIDMixin


class Market(UUIDMixin, TimestampMixin, Base):
    """A market analyzed by the Market Intelligence Agent."""

    __tablename__ = "markets"

    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    region: Mapped[str | None] = mapped_column(String(128), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    market_size_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    growth_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    market_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    attractiveness: Mapped[float | None] = mapped_column(Float, nullable=True)
    segmentation: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    analysis: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class Competitor(UUIDMixin, TimestampMixin, Base):
    """A tracked competitor."""

    __tablename__ = "competitors"

    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    website: Mapped[str | None] = mapped_column(String(512), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    threat_level: Mapped[str | None] = mapped_column(String(32), index=True, nullable=True)
    competitor_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    funding_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    employee_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pricing: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    features: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    hiring: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    updates: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class CustomerSegment(UUIDMixin, TimestampMixin, Base):
    """A customer segment analyzed by the Customer Intelligence Agent."""

    __tablename__ = "customer_segments"

    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    size_estimate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sentiment_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    pain_points: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    feature_requests: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    insights: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class Trend(UUIDMixin, TimestampMixin, Base):
    """An emerging trend detected by the Trend Intelligence Agent."""

    __tablename__ = "trends"

    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    category: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    trend_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    strength: Mapped[str | None] = mapped_column(String(32), index=True, nullable=True)
    velocity: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    forecast: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class Industry(UUIDMixin, TimestampMixin, Base):
    """An industry monitored by the Industry Intelligence Agent."""

    __tablename__ = "industries"

    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    industry_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    health: Mapped[str | None] = mapped_column(String(32), nullable=True)
    growth_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    events: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    reports: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class Opportunity(UUIDMixin, TimestampMixin, Base):
    """A growth opportunity surfaced by the Opportunity Discovery Agent."""

    __tablename__ = "opportunities"

    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)

    opportunity_score: Mapped[float | None] = mapped_column(Float, index=True, nullable=True)
    market_size_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    revenue_potential_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    competition_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    growth_potential: Mapped[float | None] = mapped_column(Float, nullable=True)
    priority: Mapped[str | None] = mapped_column(String(32), index=True, nullable=True)
    rationale: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class Risk(UUIDMixin, TimestampMixin, Base):
    """A strategic threat detected by the Risk Intelligence Agent."""

    __tablename__ = "risks"

    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(32), index=True, nullable=False)

    risk_score: Mapped[float | None] = mapped_column(Float, index=True, nullable=True)
    likelihood: Mapped[float | None] = mapped_column(Float, nullable=True)
    impact: Mapped[float | None] = mapped_column(Float, nullable=True)
    severity: Mapped[str | None] = mapped_column(String(32), index=True, nullable=True)
    timeline: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    mitigation: Mapped[dict | None] = mapped_column(JSON, nullable=True)
