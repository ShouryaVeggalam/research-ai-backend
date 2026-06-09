"""Agent 5 — Industry Intelligence Agent."""
from __future__ import annotations

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.agents.llm import summarize
from app.utils.scoring import clamp, normalize
from app.utils.text import sentiment_score


class IndustryIntelligenceAgent(BaseAgent):
    """Monitors industries: reports, events, growth, overall health."""

    name = "industry"
    description = "Monitors industries, events and growth; scores health."

    def analyze(self, context: AgentContext) -> AgentResult:
        industries = context.entities.get("industries", [])
        industry_signals = context.signals_of("industry", "regulatory")

        sentiment = (
            sum(
                sentiment_score(s.get("title", "") + " " + (s.get("content") or ""))
                for s in industry_signals
            )
            / len(industry_signals)
            if industry_signals
            else 0.0
        )

        findings: list[dict] = []
        scores: list[float] = []
        for ind in industries:
            growth = ind.get("growth_rate") or 0.0
            growth_component = clamp(normalize(growth * 100 if growth < 1 else growth, -10, 40))
            momentum = clamp(50 + sentiment * 50)
            industry_score = clamp(0.6 * growth_component + 0.4 * momentum)
            scores.append(industry_score)
            findings.append(
                {
                    "industry_id": ind.get("id"),
                    "name": ind.get("name"),
                    "industry_score": round(industry_score, 2),
                    "growth_rate": growth,
                    "health": "healthy" if industry_score >= 55 else "fragile",
                    "events": ind.get("events") or [],
                }
            )

        overall = round(sum(scores) / len(scores), 2) if scores else 0.0

        fallback = (
            f"Monitoring {len(industries)} industries with average health score {overall}. "
            f"Industry signal sentiment {round(sentiment, 2)}."
        )
        summary = summarize(
            f"Summarize the industry outlook for {context.company_name}: "
            f"industries {[f['name'] for f in findings]}, avg score {overall}.",
            fallback,
        )

        return AgentResult(
            agent=self.name,
            summary=summary,
            score=overall,
            confidence=0.75 if industries else 0.3,
            findings=findings,
            metrics={
                "industries_monitored": len(industries),
                "average_health": overall,
                "signal_sentiment": round(sentiment, 3),
            },
        )
