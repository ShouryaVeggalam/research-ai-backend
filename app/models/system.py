"""System models: alerts, activity log, notifications."""
from __future__ import annotations

from sqlalchemy import Boolean, Float, ForeignKey, String, Text
from sqlalchemy.types import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import AlertStatus
from app.database.base import Base, TimestampMixin, UUIDMixin


class Alert(UUIDMixin, TimestampMixin, Base):
    """A risk/opportunity alert raised by an engine or agent."""

    __tablename__ = "alerts"

    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    alert_type: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    priority: Mapped[str] = mapped_column(String(32), index=True, default="medium")
    severity_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    status: Mapped[str] = mapped_column(
        String(32), index=True, default=AlertStatus.OPEN.value
    )
    context: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class ActivityLog(UUIDMixin, TimestampMixin, Base):
    """Audit log of user / agent actions."""

    __tablename__ = "activity_logs"

    company_id: Mapped[str | None] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=True
    )
    user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )
    action: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    entity_type: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    entity_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    detail: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class Notification(UUIDMixin, TimestampMixin, Base):
    """A user-facing notification."""

    __tablename__ = "notifications"

    company_id: Mapped[str | None] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=True
    )
    user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
