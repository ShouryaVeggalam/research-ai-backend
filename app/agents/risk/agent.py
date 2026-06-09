"""Agent 7 — Risk Intelligence Agent."""
from __future__ import annotations

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.agents.llm import summarize
from app.core.constants import RiskCategory
from app.utils.scoring import (
    RISK_CATEGORY_WEIGHTS,
    clamp,
    risk_score,
    risk_severity,
)
from app.utils.text import keyword_overlap

_REGULATORY = {"regulation", "compliance", "ban", "fine", "lawsuit", "gdpr", "antitrust"}
_ECONOMIC = {"recession", "inflation", "downturn", "rates", "currency", "layoff"}
_TECH = {"breach", "outage", "obsolete", "disrupt", "deprecate", "vulnerability"}


class RiskIntelligenceAgent(BaseAgent):
    """Detects strategic threats across five risk categories."""

    name = "risk"
    description = "Detects market, competitive, regulatory, economic & tech risk."

    def analyze(self, context: AgentContext) -> AgentResult:
        risk_signals = context.signals_of("risk", "regulatory", "competitor", "market")
        competitor_out = context.shared.get("competitor", {})
        market_out = context.shared.get("market", {})

        corpus = " ".join(
            s.get("title", "") + " " + (s.get("content") or "") for s in risk_signals
        )

        # Category likelihoods (0-1) from signal evidence + upstream agents
        competitive_l = clamp(competitor_out.get("metrics", {}).get("max_threat_score", 30), 0, 100) / 100
        market_volatility = 1 - (clamp(market_out.get("score", 50)) / 100)
        regulatory_l = clamp(keyword_overlap(corpus, _REGULATORY) * 0.2, 0, 1)
        economic_l = clamp(keyword_overlap(corpus, _ECONOMIC) * 0.2, 0, 1)
        tech_l = clamp(keyword_overlap(corpus, _TECH) * 0.2, 0, 1)

        category_inputs = {
            RiskCategory.COMPETITIVE.value: (competitive_l, 0.8),
            RiskCategory.MARKET.value: (market_volatility, 0.7),
            RiskCategory.REGULATORY.value: (regulatory_l, 0.9),
            RiskCategory.ECONOMIC.value: (economic_l, 0.7),
            RiskCategory.TECHNOLOGY.value: (tech_l, 0.75),
        }

        findings: list[dict] = []
        heatmap: dict[str, float] = {}
        for category, (likelihood, impact) in category_inputs.items():
            score = risk_score(likelihood, impact)
            heatmap[category] = round(score, 2)
            findings.append(
                {
                    "category": category,
                    "title": f"{category.capitalize()} risk",
                    "risk_score": round(score, 2),
                    "likelihood": round(likelihood, 2),
                    "impact": round(impact, 2),
                    "severity": risk_severity(score),
                }
            )

        # persisted risks
        for r in context.entities.get("risks", []):
            findings.append(
                {
                    "category": r.get("category"),
                    "title": r.get("title"),
                    "risk_score": r.get("risk_score") or 0,
                    "likelihood": r.get("likelihood"),
                    "impact": r.get("impact"),
                    "severity": r.get("severity") or "low",
                    "source": "tracked",
                }
            )

        findings.sort(key=lambda f: f["risk_score"], reverse=True)

        aggregate = clamp(
            sum(heatmap[c] * RISK_CATEGORY_WEIGHTS[c] for c in heatmap)
        )

        fallback = (
            f"Aggregate risk index {round(aggregate, 2)}. "
            f"Top risk: {findings[0]['title'] if findings else 'n/a'} "
            f"({findings[0]['severity'] if findings else 'low'})."
        )
        summary = summarize(
            f"Summarize the strategic risk posture for {context.company_name}. "
            f"Risk heatmap: {heatmap}.",
            fallback,
        )

        return AgentResult(
            agent=self.name,
            summary=summary,
            score=round(aggregate, 2),
            confidence=0.75,
            findings=findings,
            metrics={
                "risk_heatmap": heatmap,
                "aggregate_risk": round(aggregate, 2),
                "risk_matrix": [
                    {"category": c, "likelihood": round(l, 2), "impact": round(i, 2)}
                    for c, (l, i) in category_inputs.items()
                ],
            },
            recommendations=(
                [f"Mitigate {findings[0]['title']} ({findings[0]['severity']})"]
                if findings and findings[0]["risk_score"] >= 40
                else []
            ),
        )
