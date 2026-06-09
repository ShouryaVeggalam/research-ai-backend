"""Agent 9 — Chief Research Officer (CRO) Agent — orchestrator."""
from __future__ import annotations

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.agents.llm import summarize
from app.utils.scoring import clamp


class ChiefResearchOfficerAgent(BaseAgent):
    """Synthesizes all agent outputs into an executive intelligence brief."""

    name = "cro"
    description = "Orchestrates all agents and authors the executive brief."

    def analyze(self, context: AgentContext) -> AgentResult:
        s = context.shared
        market = s.get("market", {})
        competitor = s.get("competitor", {})
        customer = s.get("customer", {})
        trend = s.get("trend", {})
        industry = s.get("industry", {})
        opportunity = s.get("opportunity", {})
        risk = s.get("risk", {})
        strategy = s.get("strategy", {})

        top_opportunities = opportunity.get("findings", [])[:5]
        top_risks = risk.get("findings", [])[:5]
        priorities = strategy.get("findings", [])[:5]

        # Strategic confidence = blend of agent confidences, penalized by risk.
        confidences = [
            market.get("confidence", 0.5),
            competitor.get("confidence", 0.5),
            customer.get("confidence", 0.5),
            trend.get("confidence", 0.5),
            industry.get("confidence", 0.5),
            opportunity.get("confidence", 0.5),
            strategy.get("confidence", 0.5),
        ]
        avg_conf = sum(confidences) / len(confidences)
        risk_penalty = (risk.get("score", 0) / 100) * 0.3
        strategic_confidence = clamp((avg_conf - risk_penalty) * 100) / 100

        # Research health score: coverage + signal richness + confidence.
        coverage = sum(
            1
            for out in (market, competitor, customer, trend, industry, opportunity, risk, strategy)
            if out.get("confidence", 0) >= 0.5
        ) / 8
        signal_richness = clamp(len(context.signals) * 2)
        research_health = clamp(
            0.4 * coverage * 100 + 0.3 * signal_richness + 0.3 * avg_conf * 100
        )

        executive_summary_fallback = (
            f"Celestra intelligence sweep for {context.company_name}: "
            f"{market.get('metrics', {}).get('markets_analyzed', 0)} markets, "
            f"{competitor.get('metrics', {}).get('competitors_tracked', 0)} competitors, "
            f"{opportunity.get('metrics', {}).get('opportunities_found', 0)} opportunities and "
            f"aggregate risk index {risk.get('score', 0)}. "
            f"Strategic confidence is {round(strategic_confidence, 2)}. "
            f"Top priority: {priorities[0]['title'] if priorities else 'establish baseline tracking'}."
        )
        executive_summary = summarize(
            "Write a concise executive intelligence brief for "
            f"{context.company_name}. Key inputs — market: {market.get('summary','')}; "
            f"competitor: {competitor.get('summary','')}; opportunity: {opportunity.get('summary','')}; "
            f"risk: {risk.get('summary','')}; strategy: {strategy.get('summary','')}.",
            executive_summary_fallback,
        )

        findings = [
            {"section": "market", "summary": market.get("summary"), "score": market.get("score")},
            {"section": "competitor", "summary": competitor.get("summary"), "score": competitor.get("score")},
            {"section": "customer", "summary": customer.get("summary"), "score": customer.get("score")},
            {"section": "trend", "summary": trend.get("summary"), "score": trend.get("score")},
            {"section": "industry", "summary": industry.get("summary"), "score": industry.get("score")},
            {"section": "opportunity", "summary": opportunity.get("summary"), "score": opportunity.get("score")},
            {"section": "risk", "summary": risk.get("summary"), "score": risk.get("score")},
            {"section": "strategy", "summary": strategy.get("summary"), "score": strategy.get("score")},
        ]

        return AgentResult(
            agent=self.name,
            summary=executive_summary,
            score=round(research_health, 2),
            confidence=round(strategic_confidence, 2),
            findings=findings,
            metrics={
                "research_health_score": round(research_health, 2),
                "strategic_confidence": round(strategic_confidence, 2),
                "top_opportunities": top_opportunities,
                "top_risks": top_risks,
                "strategic_priorities": priorities,
                "executive_recommendations": strategy.get("recommendations", []),
            },
            recommendations=strategy.get("recommendations", []),
        )
