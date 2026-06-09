"""Signal & feed repositories."""
from __future__ import annotations

from sqlalchemy import select

from app.models.signals import IntelligenceFeed, Signal
from app.repositories.base import BaseRepository


class SignalRepository(BaseRepository[Signal]):
    model = Signal

    def unprocessed(self, company_id: str, limit: int = 200) -> list[Signal]:
        stmt = (
            select(Signal)
            .where(Signal.company_id == company_id, Signal.processed.is_(False))
            .order_by(Signal.occurred_at.desc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())


class IntelligenceFeedRepository(BaseRepository[IntelligenceFeed]):
    model = IntelligenceFeed

    def latest(self, company_id: str, limit: int = 20) -> list[IntelligenceFeed]:
        return self.list(
            company_id=company_id,
            limit=limit,
            order_by=IntelligenceFeed.created_at.desc(),
        )
