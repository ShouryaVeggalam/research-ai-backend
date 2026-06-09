"""Schemas for core intelligence entities."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import RiskCategory


class _ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    company_id: str
    created_at: datetime
    updated_at: datetime


# ---------------- Market ----------------
class MarketCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    region: str | None = None
    description: str | None = None
    market_size_usd: float | None = None
    growth_rate: float | None = None


class MarketUpdate(BaseModel):
    name: str | None = None
    region: str | None = None
    description: str | None = None
    market_size_usd: float | None = None
    growth_rate: float | None = None


class MarketRead(_ORM):
    name: str
    region: str | None
    description: str | None
    market_size_usd: float | None
    growth_rate: float | None
    market_score: float | None
    attractiveness: float | None
    segmentation: dict[str, Any] | None
    analysis: dict[str, Any] | None


# ---------------- Competitor ----------------
class CompetitorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    website: str | None = None
    description: str | None = None
    funding_usd: float | None = None
    employee_count: int | None = None


class CompetitorUpdate(BaseModel):
    name: str | None = None
    website: str | None = None
    description: str | None = None
    funding_usd: float | None = None
    employee_count: int | None = None


class CompetitorRead(_ORM):
    name: str
    website: str | None
    description: str | None
    threat_level: str | None
    competitor_score: float | None
    funding_usd: float | None
    employee_count: int | None
    pricing: dict[str, Any] | None
    features: dict[str, Any] | None
    hiring: dict[str, Any] | None
    updates: dict[str, Any] | None


# ---------------- Customer Segment ----------------
class CustomerSegmentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    size_estimate: int | None = None


class CustomerSegmentRead(_ORM):
    name: str
    description: str | None
    size_estimate: int | None
    sentiment_score: float | None
    pain_points: dict[str, Any] | None
    feature_requests: dict[str, Any] | None
    insights: dict[str, Any] | None


# ---------------- Trend ----------------
class TrendCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    category: str | None = None
    description: str | None = None


class TrendRead(_ORM):
    name: str
    category: str | None
    description: str | None
    trend_score: float | None
    strength: str | None
    velocity: float | None
    confidence: float | None
    forecast: dict[str, Any] | None


# ---------------- Industry ----------------
class IndustryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None


class IndustryRead(_ORM):
    name: str
    description: str | None
    industry_score: float | None
    health: str | None
    growth_rate: float | None
    events: dict[str, Any] | None
    reports: dict[str, Any] | None


# ---------------- Opportunity ----------------
class OpportunityCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    category: str | None = None
    market_size_usd: float | None = None


class OpportunityRead(_ORM):
    title: str
    description: str | None
    category: str | None
    opportunity_score: float | None
    market_size_usd: float | None
    revenue_potential_usd: float | None
    competition_score: float | None
    growth_potential: float | None
    priority: str | None
    rationale: dict[str, Any] | None


# ---------------- Risk ----------------
class RiskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    category: RiskCategory
    likelihood: float | None = Field(default=None, ge=0, le=1)
    impact: float | None = Field(default=None, ge=0, le=1)


class RiskRead(_ORM):
    title: str
    description: str | None
    category: str
    risk_score: float | None
    likelihood: float | None
    impact: float | None
    severity: str | None
    timeline: dict[str, Any] | None
    mitigation: dict[str, Any] | None
