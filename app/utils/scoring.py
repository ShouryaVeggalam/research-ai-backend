"""Deterministic scoring helpers shared by agents & engines.

These provide a reliable, explainable baseline so the platform is fully
functional without any LLM access. When an LLM is configured the agents may
refine these scores, but the heuristics remain the ground truth fallback.
"""
from __future__ import annotations

from app.core.constants import (
    PRIORITY_WEIGHT,
    Priority,
    RiskCategory,
    ThreatLevel,
    TrendStrength,
)


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def normalize(value: float, low: float, high: float) -> float:
    """Scale ``value`` from [low, high] into [0, 100]."""
    if high <= low:
        return 0.0
    return clamp((value - low) / (high - low) * 100.0)


def weighted_score(components: dict[str, float], weights: dict[str, float]) -> float:
    """Weighted average of named components (each 0-100)."""
    total_weight = sum(weights.get(k, 0.0) for k in components)
    if total_weight == 0:
        return 0.0
    acc = sum(components[k] * weights.get(k, 0.0) for k in components)
    return clamp(acc / total_weight)


def priority_from_score(score: float) -> Priority:
    if score >= 80:
        return Priority.CRITICAL
    if score >= 60:
        return Priority.HIGH
    if score >= 35:
        return Priority.MEDIUM
    return Priority.LOW


def threat_from_score(score: float) -> ThreatLevel:
    if score >= 80:
        return ThreatLevel.SEVERE
    if score >= 60:
        return ThreatLevel.HIGH
    if score >= 35:
        return ThreatLevel.MODERATE
    return ThreatLevel.LOW


def trend_strength_from(velocity: float, score: float) -> TrendStrength:
    if velocity < 0:
        return TrendStrength.DECLINING
    if score >= 75:
        return TrendStrength.PEAKING
    if score >= 50:
        return TrendStrength.GROWING
    return TrendStrength.EMERGING


def risk_severity(score: float) -> str:
    return threat_from_score(score).value


def market_attractiveness(size_usd: float | None, growth_rate: float | None) -> float:
    """Compute a 0-100 market attractiveness from size & growth."""
    size_component = normalize((size_usd or 0) ** 0.0001 if size_usd else 0, 0, 1)
    # Use a log-like scale for size: $1M -> low, $100B -> high.
    if size_usd and size_usd > 0:
        import math

        size_component = clamp((math.log10(size_usd) - 6) / (12 - 6) * 100)
    growth_component = clamp((growth_rate or 0) * 100 if growth_rate and growth_rate < 1 else (growth_rate or 0))
    return weighted_score(
        {"size": size_component, "growth": growth_component},
        {"size": 0.45, "growth": 0.55},
    )


def opportunity_score(
    market_size_component: float,
    growth_potential: float,
    competition_score: float,
    revenue_potential_component: float,
) -> float:
    """Higher is better. Competition is inverted (less competition => higher)."""
    inverted_competition = 100 - clamp(competition_score)
    return weighted_score(
        {
            "market": clamp(market_size_component),
            "growth": clamp(growth_potential),
            "competition": inverted_competition,
            "revenue": clamp(revenue_potential_component),
        },
        {"market": 0.25, "growth": 0.3, "competition": 0.2, "revenue": 0.25},
    )


def risk_score(likelihood: float, impact: float) -> float:
    """Classic likelihood x impact, both 0-1, scaled to 0-100."""
    return clamp(likelihood * impact * 100)


# Default category weights for the aggregate risk index.
RISK_CATEGORY_WEIGHTS: dict[str, float] = {
    RiskCategory.MARKET.value: 0.22,
    RiskCategory.COMPETITIVE.value: 0.24,
    RiskCategory.REGULATORY.value: 0.16,
    RiskCategory.ECONOMIC.value: 0.18,
    RiskCategory.TECHNOLOGY.value: 0.20,
}


def aggregate_priority_weight(priorities: list[str]) -> float:
    if not priorities:
        return 0.0
    return sum(PRIORITY_WEIGHT.get(p, 1) for p in priorities) / (len(priorities) * 4) * 100
