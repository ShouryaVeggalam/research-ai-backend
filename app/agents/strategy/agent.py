"""Agent 8 — Strategy Agent."""
from __future__ import annotations

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.agents.llm import summarize
from app.utils.scoring import clamp


class StrategyAgent(BaseAgent):
    """Synthesizes upstream intelligence into prioritized recommendations.

    Answers the key strategic questions:
      - Which market should we enter?
      - What should we build next?
      - Which competitors should we watch?
      - Where is demand growing?
      - What opportunities exist?
    """

    name = "strategy"
    description = "Generates prioritized strategic recommendations & action plans."

    def analyze(self, context: AgentContext) -> AgentResult:
        market = context.shared.get("market", {})
        competitor = context.shared.get("competitor", {})
        trend = context.shared.get("trend", {})
        opportunity = context.shared.get("opportunity", {})
        risk = context.shared.get("risk", {})

        recommendations: list[dict] = []

        # Which market should we enter?
        markets = market.get("findings", [])
        if markets:
            best_market = max(markets, key=lambda m: m.get("market_score", 0))
            recommendations.append(
                {
                    "title": f"Enter {best_market.get('name')}",
                    "category": "market_entry",
                    "question": "Which market should we enter?",
                    "priority": "high" if best_market.get("market_score", 0) >= 60 else "medium",
                    "confidence": 0.8,
                    "action_plan": [
                        f"Validate demand in {best_market.get('name')}",
                        "Run a 90-day market entry pilot",
                        "Localize go-to-market positioning",
                    ],
                    "rationale": {"market_score": best_market.get("market_score")},
                }
            )

        # What should we build next?
        opps = opportunity.get("findings", [])
        product_opps = [o for o in opps if o.get("category") == "product"]
        if product_opps:
            top = product_opps[0]
            recommendations.append(
                {
                    "title": f"Build: {top.get('title')}",
                    "category": "product",
                    "question": "What should we build next?",
                    "priority": top.get("priority", "medium"),
                    "confidence": 0.7,
                    "action_plan": [
                        "Scope an MVP",
                        "Validate with 5 design partners",
                        "Define success metrics",
                    ],
                    "rationale": top.get("rationale", {}),
                }
            )

        # Which competitors should we watch?
        comp_findings = competitor.get("findings", [])
        if comp_findings:
            watch = comp_findings[0]
            recommendations.append(
                {
                    "title": f"Watch competitor: {watch.get('name')}",
                    "category": "competitive",
                    "question": "Which competitors should we watch?",
                    "priority": "high" if watch.get("competitor_score", 0) >= 60 else "medium",
                    "confidence": 0.75,
                    "action_plan": [
                        f"Set alerts on {watch.get('name')}",
                        "Benchmark feature & pricing gaps quarterly",
                    ],
                    "rationale": {"threat_level": watch.get("threat_level")},
                }
            )

        # Where is demand growing?
        trends = trend.get("findings", [])
        if trends:
            t = trends[0]
            recommendations.append(
                {
                    "title": f"Ride demand in: {t.get('name')}",
                    "category": "demand",
                    "question": "Where is demand growing?",
                    "priority": "medium",
                    "confidence": t.get("confidence", 0.6),
                    "action_plan": ["Allocate marketing toward this trend", "Publish thought leadership"],
                    "rationale": {"trend_score": t.get("trend_score")},
                }
            )

        # Risk-driven defensive recommendation
        risk_findings = risk.get("findings", [])
        if risk_findings and risk_findings[0].get("risk_score", 0) >= 40:
            r = risk_findings[0]
            recommendations.append(
                {
                    "title": f"Mitigate {r.get('title')}",
                    "category": "risk_mitigation",
                    "question": "What threatens us?",
                    "priority": "high",
                    "confidence": 0.7,
                    "action_plan": ["Assign an owner", "Define mitigation triggers", "Review monthly"],
                    "rationale": {"severity": r.get("severity")},
                }
            )

        # rank
        order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        recommendations.sort(key=lambda r: order.get(r["priority"], 3))
        for rank, r in enumerate(recommendations, start=1):
            r["priority_rank"] = rank

        confidence = clamp(
            (
                market.get("confidence", 0.5)
                + competitor.get("confidence", 0.5)
                + opportunity.get("confidence", 0.5)
            )
            / 3
            * 100,
        ) / 100

        fallback = (
            f"Generated {len(recommendations)} strategic recommendations. "
            f"Top priority: {recommendations[0]['title'] if recommendations else 'n/a'}."
        )
        summary = summarize(
            f"Write a strategy summary for {context.company_name} given these "
            f"recommendations: {[r['title'] for r in recommendations]}.",
            fallback,
        )

        return AgentResult(
            agent=self.name,
            summary=summary,
            score=round(len(recommendations) * 20, 2),
            confidence=round(confidence, 2),
            findings=recommendations,
            metrics={"recommendation_count": len(recommendations)},
            recommendations=[r["title"] for r in recommendations],
        )
