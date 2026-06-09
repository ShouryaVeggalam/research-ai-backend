"""Unit tests for the agent network and orchestrator (no DB needed)."""
from __future__ import annotations

from app.agents.base import AgentContext
from app.agents.orchestrator import run_pipeline
from app.agents.registry import AGENT_REGISTRY, PIPELINE_ORDER


def _sample_context() -> AgentContext:
    return AgentContext(
        company_id="c1",
        company_name="Acme",
        signals=[
            {
                "signal_type": "market",
                "source": "news",
                "title": "Market shows strong growth and rising demand",
                "content": "Surge in adoption and record funding.",
            },
            {
                "signal_type": "competitor",
                "source": "news",
                "title": "Rival raises funding",
                "content": "Acme Rival announced a large funding round.",
            },
            {
                "signal_type": "risk",
                "source": "news",
                "title": "New regulation and lawsuit risk",
                "content": "Potential compliance fine and antitrust concerns.",
            },
        ],
        entities={
            "markets": [
                {"id": "m1", "name": "Cloud AI", "region": "NA", "market_size_usd": 5_000_000_000, "growth_rate": 0.25}
            ],
            "competitors": [
                {"id": "k1", "name": "Acme Rival", "funding_usd": 100_000_000, "employee_count": 400}
            ],
            "customer_segments": [{"id": "s1", "name": "Enterprise", "size_estimate": 1000}],
            "trends": [],
            "industries": [{"id": "i1", "name": "SaaS", "growth_rate": 0.15}],
            "opportunities": [],
            "risks": [],
        },
    )


def test_all_agents_registered():
    assert len(AGENT_REGISTRY) == 9
    assert PIPELINE_ORDER[-1] == "cro"


def test_pipeline_runs_all_agents():
    results = run_pipeline(_sample_context())
    for name in PIPELINE_ORDER:
        assert name in results
        assert "summary" in results[name]


def test_cro_produces_strategic_confidence():
    results = run_pipeline(_sample_context())
    cro = results["cro"]
    assert 0.0 <= cro["confidence"] <= 1.0
    assert "research_health_score" in cro["metrics"]
    assert "top_opportunities" in cro["metrics"]


def test_market_agent_scores_attractive_market():
    results = run_pipeline(_sample_context())
    assert results["market"]["score"] > 0
    assert results["market"]["metrics"]["markets_analyzed"] == 1


def test_opportunity_agent_finds_opportunities():
    results = run_pipeline(_sample_context())
    assert results["opportunity"]["metrics"]["opportunities_found"] >= 1
