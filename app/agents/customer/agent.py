"""Agent 3 — Customer Intelligence Agent."""
from __future__ import annotations

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.agents.llm import summarize
from app.utils.scoring import clamp
from app.utils.text import extract_keywords, sentiment_score


class CustomerIntelligenceAgent(BaseAgent):
    """Analyzes customer behavior: segmentation, pain points, sentiment."""

    name = "customer"
    description = "Segments customers, detects pain points and sentiment."

    def analyze(self, context: AgentContext) -> AgentResult:
        segments = context.entities.get("customer_segments", [])
        feedback = context.signals_of("customer")

        feedback_text = " ".join(
            s.get("title", "") + " " + (s.get("content") or "") for s in feedback
        )
        overall_sentiment = sentiment_score(feedback_text)
        pain_points = extract_keywords(feedback_text, top_n=8) if feedback_text else []

        findings: list[dict] = []
        for seg in segments:
            seg_sentiment = seg.get("sentiment_score")
            if seg_sentiment is None:
                seg_sentiment = overall_sentiment
            findings.append(
                {
                    "segment_id": seg.get("id"),
                    "name": seg.get("name"),
                    "size_estimate": seg.get("size_estimate"),
                    "sentiment_score": round(seg_sentiment, 3),
                    "health": "positive" if seg_sentiment >= 0 else "at_risk",
                }
            )

        score = clamp(50 + overall_sentiment * 50)

        fallback = (
            f"Analyzed {len(segments)} segments and {len(feedback)} feedback signals. "
            f"Overall sentiment {round(overall_sentiment, 2)}. "
            f"Top pain points: {', '.join(pain_points[:5]) or 'none detected'}."
        )
        summary = summarize(
            f"Summarize customer intelligence for {context.company_name}: "
            f"sentiment {round(overall_sentiment, 2)}, pain points {pain_points[:5]}.",
            fallback,
        )

        return AgentResult(
            agent=self.name,
            summary=summary,
            score=round(score, 2),
            confidence=0.7 if (segments or feedback) else 0.3,
            findings=findings,
            metrics={
                "segments_analyzed": len(segments),
                "feedback_signals": len(feedback),
                "overall_sentiment": round(overall_sentiment, 3),
                "pain_points": pain_points,
                "feature_requests": pain_points[:3],
            },
            recommendations=(
                [f"Address top pain point: '{pain_points[0]}'"] if pain_points else []
            ),
        )
