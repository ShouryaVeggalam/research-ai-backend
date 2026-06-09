"""LangGraph orchestration of the intelligence agent network.

The CRO consumes all upstream agent outputs. The graph runs the agents in the
required sequence:

    Signals → Market → Competitor → Customer → Trend → Industry →
    Opportunity → Risk → Strategy → CRO

If LangGraph is unavailable for any reason, a deterministic sequential fallback
executes the exact same pipeline so orchestration always works.
"""
from __future__ import annotations

from typing import Any, TypedDict

from app.agents.base import AgentContext, AgentResult
from app.agents.registry import PIPELINE_ORDER, get_agent
from app.core.logging import get_logger

logger = get_logger("agents.orchestrator")


class GraphState(TypedDict, total=False):
    context: AgentContext
    results: dict[str, dict[str, Any]]


def _make_node(agent_name: str):
    def node(state: GraphState) -> GraphState:
        context = state["context"]
        result = get_agent(agent_name).run(context)
        results = state.get("results", {})
        results[agent_name] = result.as_dict()
        return {"context": context, "results": results}

    return node


def _build_graph():
    """Compile a LangGraph StateGraph for the pipeline, or return None."""
    try:
        from langgraph.graph import END, START, StateGraph
    except Exception as exc:  # pragma: no cover - optional dependency
        logger.warning("langgraph.unavailable", error=str(exc))
        return None

    graph = StateGraph(GraphState)
    for name in PIPELINE_ORDER:
        graph.add_node(name, _make_node(name))

    graph.add_edge(START, PIPELINE_ORDER[0])
    for prev, nxt in zip(PIPELINE_ORDER, PIPELINE_ORDER[1:]):
        graph.add_edge(prev, nxt)
    graph.add_edge(PIPELINE_ORDER[-1], END)
    return graph.compile()


_COMPILED_GRAPH = None


def _get_compiled_graph():
    global _COMPILED_GRAPH
    if _COMPILED_GRAPH is None:
        _COMPILED_GRAPH = _build_graph()
    return _COMPILED_GRAPH


def run_pipeline(context: AgentContext) -> dict[str, dict[str, Any]]:
    """Execute the full agent pipeline and return per-agent results."""
    graph = _get_compiled_graph()
    if graph is not None:
        try:
            final_state = graph.invoke({"context": context, "results": {}})
            return final_state["results"]
        except Exception as exc:  # pragma: no cover - runtime guard
            logger.warning("langgraph.invoke_failed", error=str(exc))

    # Deterministic sequential fallback.
    logger.info("orchestrator.sequential_fallback")
    results: dict[str, dict[str, Any]] = {}
    for name in PIPELINE_ORDER:
        results[name] = get_agent(name).run(context).as_dict()
    return results


def run_single(agent_name: str, context: AgentContext) -> AgentResult:
    """Run a single agent (used by per-agent API endpoints)."""
    return get_agent(agent_name).run(context)
