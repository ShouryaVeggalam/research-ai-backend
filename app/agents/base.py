"""Base classes for the intelligence agent network."""
from __future__ import annotations

import abc
from typing import Any

from pydantic import BaseModel, Field

from app.core.logging import get_logger

logger = get_logger("agents")


class AgentContext(BaseModel):
    """Input passed to every agent run.

    ``shared`` accumulates outputs from upstream agents so that downstream
    agents (Strategy, CRO) can reason over the full intelligence picture.
    """

    company_id: str
    company_name: str = "Company"
    signals: list[dict[str, Any]] = Field(default_factory=list)
    entities: dict[str, list[dict[str, Any]]] = Field(default_factory=dict)
    shared: dict[str, Any] = Field(default_factory=dict)
    params: dict[str, Any] = Field(default_factory=dict)

    def signals_of(self, *types: str) -> list[dict[str, Any]]:
        wanted = set(types)
        return [s for s in self.signals if s.get("signal_type") in wanted]


class AgentResult(BaseModel):
    """Structured output emitted by an agent."""

    agent: str
    summary: str = ""
    score: float = 0.0
    confidence: float = 0.5
    findings: list[dict[str, Any]] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)
    recommendations: list[str] = Field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return self.model_dump()


class BaseAgent(abc.ABC):
    """Abstract base for all agents.

    Subclasses implement :meth:`analyze` with deterministic heuristics. If an
    LLM is configured, :meth:`enrich` can refine the narrative summary.
    """

    name: str = "base"
    description: str = ""

    @abc.abstractmethod
    def analyze(self, context: AgentContext) -> AgentResult:
        """Produce the agent result from the given context."""

    def run(self, context: AgentContext) -> AgentResult:
        log = logger.bind(agent=self.name, company_id=context.company_id)
        log.info("agent.start")
        try:
            result = self.analyze(context)
        except Exception as exc:  # pragma: no cover - defensive
            log.error("agent.error", error=str(exc))
            return AgentResult(
                agent=self.name,
                summary=f"{self.name} agent failed: {exc}",
                confidence=0.0,
            )
        # publish into the shared context for downstream agents
        context.shared[self.name] = result.as_dict()
        log.info("agent.done", score=round(result.score, 2), confidence=result.confidence)
        return result
