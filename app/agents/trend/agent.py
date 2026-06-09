"""Agent 4 — Trend Intelligence Agent."""
from __future__ import annotations

from collections import Counter

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.agents.llm import summarize
from app.utils.scoring import clamp, normalize, trend_strength_from
from app.utils.text import extract_keywords


class TrendIntelligenceAgent(BaseAgent):
    """Detects emerging trends, classifies them, estimates velocity & forecast."""

    name = "trend"
    description = "Detects, classifies and forecasts emerging trends."

    def analyze(self, context: AgentContext) -> AgentResult:
        known_trends = context.entities.get("trends", [])
        trend_signals = context.signals_of("trend", "market", "industry")

        corpus = " ".join(
            s.get("title", "") + " " + (s.get("content") or "") for s in trend_signals
        )
        keywords = extract_keywords(corpus, top_n=12)
        freq = Counter(
            kw for s in trend_signals for kw in extract_keywords(
                s.get("title", "") + " " + (s.get("content") or ""), top_n=6
            )
        )

        findings: list[dict] = []
        scores: list[float] = []

        # incorporate persisted trends
        for t in known_trends:
            velocity = t.get("velocity") or 0.0
            base = t.get("trend_score") or 50.0
            findings.append(
                {
                    "name": t.get("name"),
                    "category": t.get("category"),
                    "trend_score": round(base, 2),
                    "velocity": velocity,
                    "strength": trend_strength_from(velocity, base).value,
                    "confidence": t.get("confidence") or 0.6,
                    "source": "tracked",
                }
            )
            scores.append(base)

        # surface detected trends from signals
        for kw, count in freq.most_common(5):
            score = clamp(normalize(count, 0, max(freq.values()) if freq else 1) * 0.8 + 20)
            velocity = round(count / max(len(trend_signals), 1), 2)
            confidence = clamp(40 + count * 10, 0, 95) / 100
            findings.append(
                {
                    "name": kw,
                    "category": "detected",
                    "trend_score": round(score, 2),
                    "velocity": velocity,
                    "strength": trend_strength_from(velocity, score).value,
                    "confidence": round(confidence, 2),
                    "mentions": count,
                    "source": "detected",
                }
            )
            scores.append(score)

        findings.sort(key=lambda f: f["trend_score"], reverse=True)
        overall = round(max(scores), 2) if scores else 0.0

        fallback = (
            f"Detected {len(findings)} trends. Strongest: "
            f"{findings[0]['name'] if findings else 'n/a'}. "
            f"Emerging keywords: {', '.join(keywords[:6]) or 'none'}."
        )
        summary = summarize(
            f"Summarize emerging trends for {context.company_name}: "
            f"top trends {[f['name'] for f in findings[:5]]}.",
            fallback,
        )

        return AgentResult(
            agent=self.name,
            summary=summary,
            score=overall,
            confidence=0.7 if findings else 0.3,
            findings=findings[:15],
            metrics={
                "trends_detected": len(findings),
                "top_keywords": keywords[:8],
                "max_trend_score": overall,
            },
            recommendations=(
                [f"Investigate emerging trend: '{findings[0]['name']}'"]
                if findings and findings[0]["trend_score"] >= 55
                else []
            ),
        )
