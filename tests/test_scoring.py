"""Unit tests for deterministic scoring helpers."""
from __future__ import annotations

from app.core.constants import Priority, ThreatLevel
from app.utils.scoring import (
    clamp,
    opportunity_score,
    priority_from_score,
    risk_score,
    threat_from_score,
)
from app.utils.text import extract_keywords, sentiment_score


def test_clamp_bounds():
    assert clamp(150) == 100
    assert clamp(-10) == 0
    assert clamp(42) == 42


def test_priority_thresholds():
    assert priority_from_score(95) == Priority.CRITICAL
    assert priority_from_score(65) == Priority.HIGH
    assert priority_from_score(40) == Priority.MEDIUM
    assert priority_from_score(10) == Priority.LOW


def test_threat_thresholds():
    assert threat_from_score(90) == ThreatLevel.SEVERE
    assert threat_from_score(10) == ThreatLevel.LOW


def test_risk_score_is_likelihood_times_impact():
    assert risk_score(0.5, 0.5) == 25.0
    assert risk_score(1.0, 1.0) == 100.0


def test_opportunity_score_rewards_low_competition():
    high = opportunity_score(80, 80, 10, 80)
    low = opportunity_score(80, 80, 90, 80)
    assert high > low


def test_sentiment_lexicon():
    assert sentiment_score("strong growth and record demand") > 0
    assert sentiment_score("lawsuit breach layoff decline") < 0


def test_extract_keywords_filters_stopwords():
    kws = extract_keywords("the market is growing and the demand is rising")
    assert "the" not in kws
    assert "market" in kws
