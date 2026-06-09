"""Repository layer — encapsulates all database access."""
from app.repositories.base import BaseRepository
from app.repositories.intelligence import (
    CompetitorRepository,
    CustomerSegmentRepository,
    IndustryRepository,
    MarketRepository,
    OpportunityRepository,
    RiskRepository,
    TrendRepository,
)
from app.repositories.reports import (
    ExecutiveBriefRepository,
    RecommendationRepository,
    ResearchReportRepository,
)
from app.repositories.signals import IntelligenceFeedRepository, SignalRepository
from app.repositories.system import (
    ActivityLogRepository,
    AlertRepository,
    NotificationRepository,
)
from app.repositories.user import CompanyRepository, UserRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "CompanyRepository",
    "MarketRepository",
    "CompetitorRepository",
    "CustomerSegmentRepository",
    "TrendRepository",
    "IndustryRepository",
    "OpportunityRepository",
    "RiskRepository",
    "SignalRepository",
    "IntelligenceFeedRepository",
    "ResearchReportRepository",
    "ExecutiveBriefRepository",
    "RecommendationRepository",
    "AlertRepository",
    "ActivityLogRepository",
    "NotificationRepository",
]
