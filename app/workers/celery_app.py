"""Celery application and beat schedule."""
from __future__ import annotations

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "celestra",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.jobs"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,
    task_soft_time_limit=540,
    worker_max_tasks_per_child=200,
)

# ---- Scheduled (beat) jobs ----
celery_app.conf.beat_schedule = {
    # Hourly refresh cycle
    "hourly-signal-refresh": {
        "task": "jobs.signal_refresh",
        "schedule": crontab(minute=0),
    },
    "hourly-trend-refresh": {
        "task": "jobs.trend_refresh",
        "schedule": crontab(minute=5),
    },
    "hourly-competitor-refresh": {
        "task": "jobs.competitor_refresh",
        "schedule": crontab(minute=10),
    },
    "hourly-opportunity-refresh": {
        "task": "jobs.opportunity_refresh",
        "schedule": crontab(minute=15),
    },
    "hourly-risk-refresh": {
        "task": "jobs.risk_refresh",
        "schedule": crontab(minute=20),
    },
    # Daily executive brief at 06:00 UTC
    "daily-executive-brief": {
        "task": "jobs.daily_executive_brief",
        "schedule": crontab(minute=0, hour=6),
    },
    # Weekly research report — Monday 07:00 UTC
    "weekly-research-report": {
        "task": "jobs.weekly_research_report",
        "schedule": crontab(minute=0, hour=7, day_of_week=1),
    },
    # Monthly strategic outlook — 1st of month 08:00 UTC
    "monthly-strategic-outlook": {
        "task": "jobs.monthly_strategic_outlook",
        "schedule": crontab(minute=0, hour=8, day_of_month=1),
    },
}
