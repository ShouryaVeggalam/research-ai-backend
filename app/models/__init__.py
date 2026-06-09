"""SQLAlchemy ORM models.

Importing this package registers every model on the shared ``Base.metadata``
so Alembic autogeneration and ``create_all`` see the full schema.
"""
from app.models.intelligence import (
    Competitor,
    CustomerSegment,
    Industry,
    Market,
    Opportunity,
    Risk,
    Trend,
)
from app.models.reports import ExecutiveBrief, Recommendation, ResearchReport
from app.models.signals import IntelligenceFeed, Signal
from app.models.system import ActivityLog, Alert, Notification
from app.models.user import Company, User

__all__ = [
    "User",
    "Company",
    "Market",
    "Competitor",
    "CustomerSegment",
    "Trend",
    "Industry",
    "Opportunity",
    "Risk",
    "Signal",
    "IntelligenceFeed",
    "ResearchReport",
    "ExecutiveBrief",
    "Recommendation",
    "Alert",
    "ActivityLog",
    "Notification",
]
