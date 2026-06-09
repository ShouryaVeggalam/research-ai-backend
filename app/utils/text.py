"""Lightweight text heuristics (sentiment, keywords) with no external deps."""
from __future__ import annotations

import re
from collections import Counter

_POSITIVE = {
    "growth", "surge", "record", "expand", "strong", "win", "lead", "innovative",
    "breakthrough", "profit", "gain", "rising", "demand", "opportunity", "success",
    "adopt", "scale", "momentum", "outperform", "raise", "funding", "launch",
}
_NEGATIVE = {
    "decline", "drop", "loss", "lawsuit", "risk", "threat", "layoff", "breach",
    "fail", "weak", "shrink", "downturn", "recession", "ban", "fine", "outage",
    "churn", "complaint", "delay", "shortage", "disrupt", "competition", "regulation",
}
_STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with", "is",
    "are", "as", "by", "at", "from", "that", "this", "it", "its", "be", "has",
    "have", "will", "we", "our", "their", "they", "you", "your", "new", "more",
}

_WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9\-]{2,}")


def tokenize(text: str) -> list[str]:
    return [w.lower() for w in _WORD_RE.findall(text or "")]


def sentiment_score(text: str) -> float:
    """Return sentiment in [-1, 1] using a simple lexicon."""
    tokens = tokenize(text)
    if not tokens:
        return 0.0
    pos = sum(1 for t in tokens if t in _POSITIVE)
    neg = sum(1 for t in tokens if t in _NEGATIVE)
    if pos + neg == 0:
        return 0.0
    return round((pos - neg) / (pos + neg), 3)


def extract_keywords(text: str, top_n: int = 8) -> list[str]:
    tokens = [t for t in tokenize(text) if t not in _STOPWORDS]
    counts = Counter(tokens)
    return [w for w, _ in counts.most_common(top_n)]


def keyword_overlap(text: str, vocabulary: set[str]) -> int:
    return len(set(tokenize(text)) & vocabulary)
