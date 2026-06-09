"""Signal ingestion pipeline.

Ingests raw signals from many sources, enriches them (sentiment, impact,
priority, entity extraction), stores them in the Signal table, and promotes
high-impact signals into the live IntelligenceFeed.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.core.constants import SignalType
from app.core.logging import get_logger
from app.models.signals import Signal
from app.repositories.signals import IntelligenceFeedRepository, SignalRepository
from app.schemas.signals import SignalCreate
from app.utils.scoring import clamp, priority_from_score
from app.utils.text import extract_keywords, sentiment_score

logger = get_logger("services.signals")

# Map signal types to feed types (1:1 here, but kept explicit for clarity).
_FEED_PROMOTION_THRESHOLD = 45.0

_SOURCE_WEIGHT: dict[str, float] = {
    "research_report": 1.0,
    "industry_report": 0.95,
    "press_release": 0.8,
    "news": 0.7,
    "company_website": 0.75,
    "finance_ai": 0.9,
    "revenue_ai": 0.9,
    "hiring_ai": 0.85,
    "internal_data": 0.85,
    "customer_feedback": 0.8,
}


class SignalService:
    def __init__(self, db: Session):
        self.db = db
        self.signals = SignalRepository(db)
        self.feed = IntelligenceFeedRepository(db)

    def _enrich(self, data: SignalCreate) -> dict[str, Any]:
        text = f"{data.title} {data.content or ''}"
        sentiment = sentiment_score(text)
        keywords = extract_keywords(text, top_n=6)
        source_weight = _SOURCE_WEIGHT.get(data.source.value, 0.7)
        # impact = base confidence * source credibility * intensity of sentiment
        intensity = abs(sentiment)
        impact = clamp((0.5 + 0.5 * intensity) * source_weight * (0.5 + data.confidence) * 100)
        priority = priority_from_score(impact).value
        return {
            "sentiment": sentiment,
            "entities": {"keywords": keywords},
            "impact_score": round(impact, 2),
            "priority": priority,
        }

    def ingest_one(self, company_id: str, data: SignalCreate, *, commit: bool = True) -> Signal:
        enrichment = self._enrich(data)
        signal = self.signals.create(
            company_id=company_id,
            title=data.title,
            content=data.content,
            url=data.url,
            signal_type=data.signal_type.value,
            source=data.source.value,
            confidence=data.confidence,
            raw_payload=data.raw_payload,
            occurred_at=data.occurred_at or datetime.now(timezone.utc),
            processed=True,
            **enrichment,
        )
        # Promote high-impact signals to the live feed.
        if signal.impact_score >= _FEED_PROMOTION_THRESHOLD:
            self._promote_to_feed(signal)
        if commit:
            self.db.commit()
            self.db.refresh(signal)
        return signal

    def ingest_batch(self, company_id: str, items: list[SignalCreate]) -> list[Signal]:
        created = [self.ingest_one(company_id, item, commit=False) for item in items]
        self.db.commit()
        for s in created:
            self.db.refresh(s)
        logger.info("signals.ingested", company_id=company_id, count=len(created))
        return created

    def _promote_to_feed(self, signal: Signal):
        return self.feed.create(
            company_id=signal.company_id,
            signal_id=signal.id,
            title=signal.title,
            summary=signal.content,
            feed_type=signal.signal_type,
            priority=signal.priority,
            confidence=signal.confidence,
            impact_score=signal.impact_score,
            payload=signal.entities,
        )

    def list_signals(self, company_id: str, *, offset: int = 0, limit: int = 50, signal_type: str | None = None):
        filters: dict[str, Any] = {"company_id": company_id}
        if signal_type:
            filters["signal_type"] = signal_type
        items = self.signals.list(offset=offset, limit=limit, **filters)
        total = self.signals.count(**filters)
        return items, total
