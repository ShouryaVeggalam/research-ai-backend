"""Signal ingestion and live intelligence feed models."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.types import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin, UUIDMixin


class Signal(UUIDMixin, TimestampMixin, Base):
    """A raw intelligence signal ingested from an external/internal source."""

    __tablename__ = "signals"

    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    signal_type: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    source: Mapped[str] = mapped_column(String(64), index=True, nullable=False)

    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    impact_score: Mapped[float] = mapped_column(Float, default=0.0)
    priority: Mapped[str] = mapped_column(String(32), index=True, default="medium")
    sentiment: Mapped[float | None] = mapped_column(Float, nullable=True)

    raw_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    entities: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    processed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )


class IntelligenceFeed(UUIDMixin, TimestampMixin, Base):
    """A processed, prioritized feed item surfaced in the live feed."""

    __tablename__ = "intelligence_feed"

    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    signal_id: Mapped[str | None] = mapped_column(
        ForeignKey("signals.id", ondelete="SET NULL"), nullable=True
    )

    title: Mapped[str] = mapped_column(String(512), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    feed_type: Mapped[str] = mapped_column(String(32), index=True, nullable=False)

    priority: Mapped[str] = mapped_column(String(32), index=True, default="medium")
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    impact_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)

    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
