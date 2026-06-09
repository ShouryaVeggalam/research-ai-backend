"""Signal ingestion endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Query

from app.api.deps import CompanyId, CurrentUser, RequireAnalyst, DbSession
from app.schemas.common import PaginatedResponse
from app.schemas.signals import SignalCreate, SignalIngestBatch, SignalRead
from app.services.signal_service import SignalService

router = APIRouter(prefix="/signals", tags=["signals"])


@router.post("/ingest", response_model=SignalRead, status_code=201)
def ingest_signal(payload: SignalCreate, db: DbSession, company_id: CompanyId, _: RequireAnalyst):
    signal = SignalService(db).ingest_one(company_id, payload)
    return SignalRead.model_validate(signal)


@router.post("/ingest/batch", response_model=list[SignalRead], status_code=201)
def ingest_batch(payload: SignalIngestBatch, db: DbSession, company_id: CompanyId, _: RequireAnalyst):
    signals = SignalService(db).ingest_batch(company_id, payload.signals)
    return [SignalRead.model_validate(s) for s in signals]


@router.get("", response_model=PaginatedResponse[SignalRead])
def list_signals(
    db: DbSession,
    company_id: CompanyId,
    _: CurrentUser,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    signal_type: str | None = Query(None),
):
    items, total = SignalService(db).list_signals(
        company_id, offset=(page - 1) * size, limit=size, signal_type=signal_type
    )
    return PaginatedResponse[SignalRead](
        items=[SignalRead.model_validate(i) for i in items],
        total=total,
        page=page,
        size=size,
    )
