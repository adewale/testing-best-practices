"""Pick keyphrases from a comma-separated list, strongest first."""
from __future__ import annotations

from functools import cmp_to_key

MIN_SCORE = 4.0
_CACHE: dict[str, float] = {}


def _score(phrase: str) -> float:
    """Average word length. Cached because callers score the same phrases often."""
    if phrase in _CACHE:
        return _CACHE[phrase]
    words = phrase.split()
    value = sum(len(w) for w in words) / len(words)
    _CACHE[phrase] = value
    return value


def _before(a: tuple[str, float], b: tuple[str, float]) -> bool:
    """Higher score first; alphabetical among equal scores."""
    if a[1] != b[1]:
        return a[1] > b[1]
    return a[0] < b[0]


def _cmp(a: tuple[str, float], b: tuple[str, float]) -> int:
    return -1 if _before(a, b) else 1


def top_phrases(text: str, limit: int = 5) -> list[str]:
    """Distinct phrases (case-insensitive) scoring at least MIN_SCORE, strongest first."""
    seen: set[str] = set()
    scored: list[tuple[str, float]] = []
    for raw in text.split(","):
        phrase = " ".join(raw.split())
        if not phrase or phrase.lower() in seen:
            continue
        seen.add(phrase.lower())
        score = _score(phrase)
        if score >= MIN_SCORE:
            scored.append((phrase, score))
    scored.sort(key=cmp_to_key(_cmp))
    return [p for p, _ in scored[:limit]]
