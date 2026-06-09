"""Agent 1 — Market Intelligence Agent."""
from __future__ import annotations

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.agents.llm import summarize
from app.utils.scoring import clamp, market_attractiveness
from app.utils.text import sentiment_score


class MarketIntelligenceAgent(BaseAgent):
    """Analyzes markets: size, growth, segmentation, regional attractiveness."""

    name = "market"
    description = "Analyzes markets, growth, size, segmentation and regions."

    def analyze(self, context: AgentContext) -> AgentResult:
        markets = context.entities.get("markets", [])
        market_signals = context.signals_of("market")

        findings: list[dict] = []
        scores: list[float] = []

        signal_sentiment = (
            sum(sentiment_score(s.get("title", "") + " " + (s.get("content") or "")) for s in market_signals)
            / len(market_signals)
            if market_signals
            else 0.0
        )

        for m in markets:
            attractiveness = market_attractiveness(
                m.get("market_size_usd"), m.get("growth_rate")
            )
            # signal momentum nudges the score
            momentum = clamp(50 + signal_sentiment * 50)
            market_score = clamp(0.7 * attractiveness + 0.3 * momentum)
            scores.append(market_score)
            findings.append(
                {
                    "market_id": m.get("id"),
                    "name": m.get("name"),
                    "region": m.get("region"),
                    "market_score": round(market_score, 2),
                    "attractiveness": round(attractiveness, 2),
                    "growth_rate": m.get("growth_rate"),
                    "market_size_usd": m.get("market_size_usd"),
                    "segmentation": {
                        "enterprise": 0.4,
                        "mid_market": 0.35,
                        "smb": 0.25,
                    },
                }
            )

        overall = round(sum(scores) / len(scores), 2) if scores else 0.0
        growth_rates = [m.get("growth_rate") for m in markets if m.get("growth_rate")]
        avg_growth = round(sum(growth_rates) / len(growth_rates), 4) if growth_rates else 0.0

        fallback = (
            f"Tracking {len(markets)} markets with an average attractiveness of {overall}. "
            f"Average growth rate is {avg_growth}. Market signal sentiment is "
            f"{'positive' if signal_sentiment > 0 else 'neutral/negative'}."
        )
        summary = summarize(
            f"Summarize the market landscape for {context.company_name}. "
            f"Markets analyzed: {[f.get('name') for f in findings]}. "
            f"Overall score {overall}, avg growth {avg_growth}.",
            fallback,
        )

        return AgentResult(
            agent=self.name,
            summary=summary,
            score=overall,
            confidence=0.8 if markets else 0.3,
            findings=findings,
            metrics={
                "markets_analyzed": len(markets),
                "average_growth_rate": avg_growth,
                "signal_sentiment": round(signal_sentiment, 3),
                "market_score": overall,
            },
            recommendations=(
                [f"Prioritize entry into {findings[0]['name']}" ]
                if findings and findings[0]["market_score"] >= 60
                else []
            ),
        )
