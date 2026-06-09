"""Live intelligence feed — REST + WebSocket."""
from __future__ import annotations

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.api.deps import CompanyId, CurrentUser, DbSession
from app.core.security import ACCESS_TOKEN, decode_token
from app.database.session import SessionLocal
from app.repositories.user import UserRepository
from app.schemas.common import PaginatedResponse
from app.schemas.signals import FeedItemRead
from app.services.feed_service import FeedService, stream_feed

router = APIRouter(prefix="/feed", tags=["feed"])


@router.get("", response_model=PaginatedResponse[FeedItemRead])
def list_feed(
    db: DbSession,
    company_id: CompanyId,
    _: CurrentUser,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    feed_type: str | None = Query(None),
):
    items, total = FeedService(db).latest(company_id, limit=size, feed_type=feed_type)
    return PaginatedResponse[FeedItemRead](
        items=[FeedItemRead.model_validate(i) for i in items],
        total=total,
        page=page,
        size=size,
    )


@router.post("/{feed_id}/read", response_model=FeedItemRead)
def mark_read(feed_id: str, db: DbSession, company_id: CompanyId, _: CurrentUser):
    item = FeedService(db).mark_read(company_id, feed_id)
    return FeedItemRead.model_validate(item)


@router.websocket("/ws")
async def feed_ws(websocket: WebSocket, token: str = Query(...)):
    """Stream live feed updates.

    Authenticate by passing a valid access token as the ``token`` query
    parameter: ``ws://host/api/v1/feed/ws?token=<JWT>``.
    """
    try:
        payload = decode_token(token, expected_type=ACCESS_TOKEN)
        with SessionLocal() as db:
            user = UserRepository(db).get(payload["sub"])
            company_id = user.company_id if user else None
        if not company_id:
            await websocket.close(code=4401)
            return
    except Exception:
        await websocket.close(code=4401)
        return

    try:
        await stream_feed(company_id, websocket)
    except WebSocketDisconnect:
        pass
