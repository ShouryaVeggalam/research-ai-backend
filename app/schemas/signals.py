"""Signal & feed schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import SignalSource, SignalType


class SignalCreate(BaseModel):
    title: str = Field(min_length=1, max_length=512)
    content: str | None = None
    url: str | None = None
    signal_type: SignalType
    source: SignalSource
    confidence: float = Field(default=0.5, ge=0, le=1)
    raw_payload: dict[str, Any] | None = None
    occurred_at: datetime | None = None


class SignalIngestBatch(BaseModel):
    signals: list[SignalCreate] = Field(min_length=1, max_length=500)


class SignalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    title: str
    content: str | None
    url: str | None
    signal_type: str
    source: str
    confidence: float
    impact_score: float
    priority: str
    sentiment: float | None
    entities: dict[str, Any] | None
    processed: bool
    occurred_at: datetime
    created_at: datetime


class FeedItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    signal_id: str | None
    title: str
    summary: str | None
    feed_type: str
    priority: str
    confidence: float
    impact_score: float
    payload: dict[str, Any] | None
    is_read: bool
    created_at: datetime


class FeedEvent(BaseModel):
    """WebSocket payload broadcast to live-feed subscribers."""

    event: str = "feed.update"
    item: FeedItemRead
