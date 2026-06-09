"""Optional LLM client for narrative enrichment.

Agents stay fully functional without an LLM. When ``settings.llm_active`` is
true, :func:`get_llm` returns a configured LangChain ChatOpenAI client that
agents can use to generate executive narratives.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("agents.llm")


@lru_cache
def get_llm() -> Any | None:
    """Return a LangChain chat model, or ``None`` when LLM use is disabled."""
    if not settings.llm_active:
        return None
    try:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            temperature=settings.LLM_TEMPERATURE,
            timeout=30,
            max_retries=2,
        )
    except Exception as exc:  # pragma: no cover - optional dependency path
        logger.warning("llm.init_failed", error=str(exc))
        return None


def summarize(prompt: str, fallback: str) -> str:
    """Generate a short narrative, gracefully falling back to ``fallback``."""
    llm = get_llm()
    if llm is None:
        return fallback
    try:
        from langchain_core.messages import HumanMessage, SystemMessage

        messages = [
            SystemMessage(
                content=(
                    "You are a senior strategy analyst at Celestra Research AI. "
                    "Write concise, executive-grade intelligence summaries."
                )
            ),
            HumanMessage(content=prompt),
        ]
        response = llm.invoke(messages)
        return str(getattr(response, "content", fallback)).strip() or fallback
    except Exception as exc:  # pragma: no cover - network/runtime guard
        logger.warning("llm.summarize_failed", error=str(exc))
        return fallback
