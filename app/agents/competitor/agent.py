"""Agent 2 — Competitor Intelligence Agent."""
from __future__ import annotations

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.agents.llm import summarize
from app.utils.scoring import clamp, normalize, threat_from_score


class CompetitorIntelligenceAgent(BaseAgent):
    """Tracks competitors: features, pricing, funding, hiring; scores threat."""

    name = "competitor"
    description = "Monitors competitors and scores their strategic threat."

    def analyze(self, context: AgentContext) -> AgentResult:
        competitors = context.entities.get("competitors", [])
        comp_signals = context.signals_of("competitor", "funding")

        # index recent signals to competitor names
        signals_by_name: dict[str, int] = {}
        for s in comp_signals:
            text = (s.get("title", "") + " " + (s.get("content") or "")).lower()
            for c in competitors:
                if c.get("name", "").lower() in text:
                    signals_by_name[c["name"]] = signals_by_name.get(c["name"], 0) + 1

        findings: list[dict] = []
        scores: list[float] = []
        for c in competitors:
            funding = c.get("funding_usd") or 0
            employees = c.get("employee_count") or 0
            funding_component = normalize(funding, 0, 500_000_000)
            size_component = normalize(employees, 0, 5000)
            activity = clamp(signals_by_name.get(c.get("name", ""), 0) * 20)
            threat_score = clamp(
                0.4 * funding_component + 0.3 * size_component + 0.3 * activity
            )
            scores.append(threat_score)
            findings.append(
                {
                    "competitor_id": c.get("id"),
                    "name": c.get("name"),
                    "competitor_score": round(threat_score, 2),
                    "threat_level": threat_from_score(threat_score).value,
                    "funding_usd": funding,
                    "employee_count": employees,
                    "recent_signals": signals_by_name.get(c.get("name", ""), 0),
                    "updates": {
                        "feature_changes": activity > 0,
                        "pricing_changes": False,
                        "hiring_surge": size_component > 60,
                    },
                }
            )

        findings.sort(key=lambda f: f["competitor_score"], reverse=True)
        overall = round(max(scores), 2) if scores else 0.0

        fallback = (
            f"Tracking {len(competitors)} competitors. Highest threat: "
            f"{findings[0]['name'] if findings else 'n/a'} "
            f"({findings[0]['threat_level'] if findings else 'n/a'})."
        )
        summary = summarize(
            f"Summarize the competitive landscape for {context.company_name}. "
            f"Top competitors by threat: {[f['name'] for f in findings[:3]]}.",
            fallback,
        )

        return AgentResult(
            agent=self.name,
            summary=summary,
            score=overall,
            confidence=0.8 if competitors else 0.3,
            findings=findings,
            metrics={
                "competitors_tracked": len(competitors),
                "max_threat_score": overall,
                "active_competitors": len(signals_by_name),
            },
            recommendations=(
                [f"Closely monitor {findings[0]['name']} (threat: {findings[0]['threat_level']})"]
                if findings and findings[0]["competitor_score"] >= 60
                else []
            ),
        )
