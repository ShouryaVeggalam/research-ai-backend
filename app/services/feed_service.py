"""Live intelligence feed service + WebSocket connection manager."""
from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.database.session import SessionLocal
from app.models.signals import IntelligenceFeed
from app.repositories.signals import IntelligenceFeedRepository

logger = get_logger("services.feed")


class FeedService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = IntelligenceFeedRepository(db)

    def latest(self, company_id: str, *, limit: int = 20, feed_type: str | None = None):
        filters: dict[str, Any] = {"company_id": company_id}
        if feed_type:
            filters["feed_type"] = feed_type
        items = self.repo.list(limit=limit, **filters)
        total = self.repo.count(**filters)
        return items, total

    def mark_read(self, company_id: str, feed_id: str) -> IntelligenceFeed | None:
        obj = self.repo.get(feed_id)
        if obj and obj.company_id == company_id:
            self.repo.update(obj, is_read=True)
            self.db.commit()
        return obj

    def items_since(self, company_id: str, since: datetime) -> list[IntelligenceFeed]:
        stmt = (
            select(IntelligenceFeed)
            .where(
                IntelligenceFeed.company_id == company_id,
                IntelligenceFeed.created_at > since,
            )
            .order_by(IntelligenceFeed.created_at.asc())
        )
        return list(self.db.execute(stmt).scalars().all())


class ConnectionManager:
    """Tracks active WebSocket connections per company."""

    def __init__(self) -> None:
        self._connections: dict[str, set[Any]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, company_id: str, websocket: Any) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections.setdefault(company_id, set()).add(websocket)
        logger.info("feed.ws_connected", company_id=company_id)

    async def disconnect(self, company_id: str, websocket: Any) -> None:
        async with self._lock:
            conns = self._connections.get(company_id)
            if conns:
                conns.discard(websocket)
                if not conns:
                    self._connections.pop(company_id, None)

    async def broadcast(self, company_id: str, message: dict[str, Any]) -> None:
        async with self._lock:
            conns = list(self._connections.get(company_id, set()))
        for ws in conns:
            try:
                await ws.send_json(message)
            except Exception:  # pragma: no cover - drop dead connections
                await self.disconnect(company_id, ws)


manager = ConnectionManager()


async def stream_feed(company_id: str, websocket: Any, *, poll_interval: float = 3.0) -> None:
    """Push new feed items to a connected client by polling the DB.

    A pragmatic real-time mechanism that works across API + worker processes
    without extra infrastructure. Uses its own DB session.
    """
    from app.schemas.signals import FeedItemRead

    await manager.connect(company_id, websocket)
    last_seen = datetime.utcnow()
    try:
        # send a snapshot of the latest items on connect
        with SessionLocal() as db:
            service = FeedService(db)
            items, _ = service.latest(company_id, limit=10)
            for item in reversed(items):
                await websocket.send_json(
                    {"event": "feed.snapshot", "item": FeedItemRead.model_validate(item).model_dump(mode="json")}
                )

        while True:
            await asyncio.sleep(poll_interval)
            with SessionLocal() as db:
                service = FeedService(db)
                new_items = service.items_since(company_id, last_seen)
            if new_items:
                last_seen = new_items[-1].created_at.replace(tzinfo=None)
                for item in new_items:
                    await websocket.send_json(
                        {"event": "feed.update", "item": FeedItemRead.model_validate(item).model_dump(mode="json")}
                    )
    except Exception as exc:  # pragma: no cover - client disconnect path
        logger.info("feed.ws_closed", company_id=company_id, reason=str(exc))
    finally:
        await manager.disconnect(company_id, websocket)
