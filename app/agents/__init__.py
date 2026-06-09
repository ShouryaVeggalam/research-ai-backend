"""Celestra intelligence agent network.

Nine specialized agents collaborate, orchestrated by the Chief Research
Officer (CRO) agent via a LangGraph workflow:

    Market → Competitor → Customer → Trend → Industry →
    Opportunity → Risk → Strategy → CRO
"""
from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.agents.registry import AGENT_REGISTRY, get_agent

__all__ = ["AgentContext", "AgentResult", "BaseAgent", "AGENT_REGISTRY", "get_agent"]
