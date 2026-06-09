"""Alert, activity log & notification repositories."""
from __future__ import annotations

from sqlalchemy import select

from app.core.constants import AlertStatus
from app.models.system import ActivityLog, Alert, Notification
from app.repositories.base import BaseRepository


class AlertRepository(BaseRepository[Alert]):
    model = Alert

    def open_alerts(self, company_id: str, limit: int = 50) -> list[Alert]:
        stmt = (
            select(Alert)
            .where(Alert.company_id == company_id, Alert.status == AlertStatus.OPEN.value)
            .order_by(Alert.severity_score.desc().nullslast())
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())


class ActivityLogRepository(BaseRepository[ActivityLog]):
    model = ActivityLog


class NotificationRepository(BaseRepository[Notification]):
    model = Notification

    def for_user(self, user_id: str, limit: int = 50) -> list[Notification]:
        return self.list(
            user_id=user_id, limit=limit, order_by=Notification.created_at.desc()
        )
