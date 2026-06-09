"""Agent 6 — Opportunity Discovery Agent."""
from __future__ import annotations

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.agents.llm import summarize
from app.utils.scoring import (
    clamp,
    normalize,
    opportunity_score,
    priority_from_score,
)


class OpportunityDiscoveryAgent(BaseAgent):
    """Finds growth opportunities via gap analysis and ranks them."""

    name = "opportunity"
    description = "Performs gap analysis and ranks growth opportunities."

    def analyze(self, context: AgentContext) -> AgentResult:
        market_out = context.shared.get("market", {})
        competitor_out = context.shared.get("competitor", {})
        trend_out = context.shared.get("trend", {})
        customer_out = context.shared.get("customer", {})

        persisted = context.entities.get("opportunities", [])

        findings: list[dict] = []

        # Opportunities derived from attractive markets with low competition
        market_findings = market_out.get("findings", [])
        max_threat = competitor_out.get("metrics", {}).get("max_threat_score", 50)
        for mf in market_findings:
            market_component = mf.get("market_score", 50)
            growth_potential = clamp((mf.get("growth_rate") or 0) * 100 if (mf.get("growth_rate") or 0) < 1 else (mf.get("growth_rate") or 0))
            competition = max_threat
            revenue_component = normalize(mf.get("market_size_usd") or 0, 0, 10_000_000_000)
            score = opportunity_score(market_component, growth_potential, competition, revenue_component)
            findings.append(
                {
                    "title": f"Expand into {mf.get('name')}",
                    "category": "market",
                    "opportunity_score": round(score, 2),
                    "market_size_usd": mf.get("market_size_usd"),
                    "revenue_potential_usd": (mf.get("market_size_usd") or 0) * 0.02,
                    "competition_score": round(competition, 2),
                    "growth_potential": round(growth_potential, 2),
                    "priority": priority_from_score(score).value,
                    "rationale": {"driver": "attractive market", "source_market": mf.get("name")},
                }
            )

        # Opportunities derived from strong trends
        for tf in trend_out.get("findings", [])[:3]:
            score = clamp(0.7 * tf.get("trend_score", 50) + 20)
            findings.append(
                {
                    "title": f"Build for trend: {tf.get('name')}",
                    "category": "product",
                    "opportunity_score": round(score, 2),
                    "revenue_potential_usd": None,
                    "competition_score": round(max_threat, 2),
                    "growth_potential": round(tf.get("trend_score", 50), 2),
                    "priority": priority_from_score(score).value,
                    "rationale": {"driver": "emerging trend", "trend": tf.get("name")},
                }
            )

        # Opportunities derived from customer pain points
        for pain in customer_out.get("metrics", {}).get("pain_points", [])[:3]:
            score = 55.0
            findings.append(
                {
                    "title": f"Solve customer pain: {pain}",
                    "category": "product",
                    "opportunity_score": score,
                    "revenue_potential_usd": None,
                    "competition_score": round(max_threat, 2),
                    "growth_potential": 50.0,
                    "priority": priority_from_score(score).value,
                    "rationale": {"driver": "customer pain point", "pain_point": pain},
                }
            )

        for op in persisted:
            findings.append(
                {
                    "title": op.get("title"),
                    "category": op.get("category") or "market",
                    "opportunity_score": op.get("opportunity_score") or 50.0,
                    "market_size_usd": op.get("market_size_usd"),
                    "revenue_potential_usd": op.get("revenue_potential_usd"),
                    "competition_score": op.get("competition_score") or max_threat,
                    "growth_potential": op.get("growth_potential") or 50.0,
                    "priority": op.get("priority") or "medium",
                    "rationale": op.get("rationale") or {"driver": "tracked"},
                }
            )

        findings.sort(key=lambda f: f["opportunity_score"], reverse=True)
        for rank, f in enumerate(findings, start=1):
            f["priority_rank"] = rank

        overall = round(findings[0]["opportunity_score"], 2) if findings else 0.0

        fallback = (
            f"Discovered {len(findings)} opportunities. Top: "
            f"{findings[0]['title'] if findings else 'n/a'} "
            f"(score {overall})."
        )
        summary = summarize(
            f"Summarize the top growth opportunities for {context.company_name}: "
            f"{[f['title'] for f in findings[:5]]}.",
            fallback,
        )

        return AgentResult(
            agent=self.name,
            summary=summary,
            score=overall,
            confidence=0.7 if findings else 0.3,
            findings=findings[:20],
            metrics={"opportunities_found": len(findings), "top_score": overall},
            recommendations=[f["title"] for f in findings[:3]],
        )
