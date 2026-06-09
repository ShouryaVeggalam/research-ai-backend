"""Alert & notification schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AlertRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    title: str
    message: str | None
    alert_type: str
    priority: str
    severity_score: float | None
    status: str
    context: dict[str, Any] | None
    created_at: datetime


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str | None
    title: str
    body: str | None
    category: str | None
    is_read: bool
    payload: dict[str, Any] | None
    created_at: datetime
