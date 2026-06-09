"""Central registry of all agents in the network."""
from __future__ import annotations

from app.agents.base import BaseAgent
from app.agents.competitor import CompetitorIntelligenceAgent
from app.agents.cro import ChiefResearchOfficerAgent
from app.agents.customer import CustomerIntelligenceAgent
from app.agents.industry import IndustryIntelligenceAgent
from app.agents.market import MarketIntelligenceAgent
from app.agents.opportunity import OpportunityDiscoveryAgent
from app.agents.risk import RiskIntelligenceAgent
from app.agents.strategy import StrategyAgent
from app.agents.trend import TrendIntelligenceAgent

# Ordered to match the intelligence pipeline.
AGENT_REGISTRY: dict[str, BaseAgent] = {
    "market": MarketIntelligenceAgent(),
    "competitor": CompetitorIntelligenceAgent(),
    "customer": CustomerIntelligenceAgent(),
    "trend": TrendIntelligenceAgent(),
    "industry": IndustryIntelligenceAgent(),
    "opportunity": OpportunityDiscoveryAgent(),
    "risk": RiskIntelligenceAgent(),
    "strategy": StrategyAgent(),
    "cro": ChiefResearchOfficerAgent(),
}

PIPELINE_ORDER: list[str] = list(AGENT_REGISTRY.keys())


def get_agent(name: str) -> BaseAgent:
    if name not in AGENT_REGISTRY:
        raise KeyError(f"Unknown agent: {name}")
    return AGENT_REGISTRY[name]
