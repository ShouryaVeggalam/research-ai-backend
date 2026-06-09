"""Alerts & notifications endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Query

from app.api.deps import CompanyId, CurrentUser, DbSession
from app.core.constants import AlertStatus
from app.repositories.system import AlertRepository, NotificationRepository
from app.schemas.system import AlertRead, NotificationRead

alerts_router = APIRouter(prefix="/alerts", tags=["alerts"])
notifications_router = APIRouter(prefix="/notifications", tags=["notifications"])


@alerts_router.get("", response_model=list[AlertRead])
def list_alerts(
    db: DbSession,
    company_id: CompanyId,
    _: CurrentUser,
    only_open: bool = Query(True),
    limit: int = Query(50, ge=1, le=200),
):
    repo = AlertRepository(db)
    items = repo.open_alerts(company_id, limit=limit) if only_open else repo.list(
        company_id=company_id, limit=limit
    )
    return [AlertRead.model_validate(i) for i in items]


@alerts_router.post("/{alert_id}/acknowledge", response_model=AlertRead)
def acknowledge(alert_id: str, db: DbSession, company_id: CompanyId, _: CurrentUser):
    repo = AlertRepository(db)
    obj = repo.get(alert_id)
    if obj and obj.company_id == company_id:
        repo.update(obj, status=AlertStatus.ACKNOWLEDGED.value)
        db.commit()
        db.refresh(obj)
    return AlertRead.model_validate(obj)


@notifications_router.get("", response_model=list[NotificationRead])
def list_notifications(db: DbSession, user: CurrentUser, limit: int = Query(50, ge=1, le=200)):
    items = NotificationRepository(db).for_user(user.id, limit=limit)
    return [NotificationRead.model_validate(i) for i in items]
