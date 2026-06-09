"""Domain enums and constants shared across the platform."""
from __future__ import annotations

from enum import Enum


class UserRole(str, Enum):
    """Role-based access control roles, ordered by privilege."""

    ADMIN = "admin"
    FOUNDER = "founder"
    RESEARCH_MANAGER = "research_manager"
    ANALYST = "analyst"
    VIEWER = "viewer"


# Hierarchy: higher number => more privilege.
ROLE_HIERARCHY: dict[str, int] = {
    UserRole.VIEWER: 1,
    UserRole.ANALYST: 2,
    UserRole.RESEARCH_MANAGER: 3,
    UserRole.FOUNDER: 4,
    UserRole.ADMIN: 5,
}


class SignalType(str, Enum):
    COMPETITOR = "competitor"
    MARKET = "market"
    TREND = "trend"
    OPPORTUNITY = "opportunity"
    RISK = "risk"
    FUNDING = "funding"
    REGULATORY = "regulatory"
    CUSTOMER = "customer"
    INDUSTRY = "industry"


class SignalSource(str, Enum):
    NEWS = "news"
    RESEARCH_REPORT = "research_report"
    INDUSTRY_REPORT = "industry_report"
    COMPANY_WEBSITE = "company_website"
    PRESS_RELEASE = "press_release"
    CUSTOMER_FEEDBACK = "customer_feedback"
    INTERNAL_DATA = "internal_data"
    REVENUE_AI = "revenue_ai"
    FINANCE_AI = "finance_ai"
    HIRING_AI = "hiring_ai"


class Priority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ThreatLevel(str, Enum):
    SEVERE = "severe"
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"


class RiskCategory(str, Enum):
    MARKET = "market"
    COMPETITIVE = "competitive"
    REGULATORY = "regulatory"
    ECONOMIC = "economic"
    TECHNOLOGY = "technology"


class ReportType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    AD_HOC = "ad_hoc"


class TrendStrength(str, Enum):
    EMERGING = "emerging"
    GROWING = "growing"
    PEAKING = "peaking"
    DECLINING = "declining"


class AlertStatus(str, Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


PRIORITY_WEIGHT: dict[str, int] = {
    Priority.CRITICAL: 4,
    Priority.HIGH: 3,
    Priority.MEDIUM: 2,
    Priority.LOW: 1,
}
