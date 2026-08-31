#!/usr/bin/env python3
"""E66 oracle: distinguish test artifacts from executed, production-reaching work."""
from __future__ import annotations

import re
import sys
from pathlib import Path

NEGATED = re.compile(
    r"(?:\b(?:do|does|did|should|must|need|can|could|will|would)\s+not\b"
    r"|\b(?:don.t|doesn.t|didn.t|shouldn.t|mustn.t|needn.t|can.t|cannot|"
    r"couldn.t|won.t|wouldn.t)\b|\bnot\b|\bnever\b|\bwithout\b|\bno\s+need\s+to\b)"
    r"(?:\W+\w+){0,6}\W*$",
    re.IGNORECASE,
)


def read_markdown(root: Path) -> str:
    return "\n".join(p.read_text(errors="ignore") for p in root.rglob("*.md"))


def has(pattern: str, text: str) -> bool:
    return re.search(pattern, text, re.IGNORECASE | re.DOTALL) is not None


def negated_before(text: str, start: int) -> bool:
    prefix = text[max(0, start - 140) : start]
    prefix = re.split(r"(?<=[.!?;])\s+", prefix)[-1]
    return NEGATED.search(prefix) is not None


def affirmed(pattern: str, text: str) -> bool:
    return any(
        not negated_before(text, match.start())
        for match in re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
    )


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    low = read_markdown(root).lower()
    errors: list[str] = []
    if not low.strip():
        print("no markdown assessment found", file=sys.stderr)
        return 1

    python_diagnosis = has(
        r"unittest.{0,180}(does not|doesn.t|won.t|will not|cannot|zero).{0,180}"
        r"(collect|discover|run).{0,100}(module.?level|pytest|hypothesis|function)"
        r"|(module.?level|pytest|hypothesis).{0,160}(not|isn.t).{0,60}"
        r"(collect|discover|run).{0,100}unittest",
        low,
    )
    pytest_runner = affirmed(
        r"\b(run|use|switch|migrate|move)\b.{0,100}\bpytest\b",
        low,
    )
    pytest_guard = affirmed(
        r"\b(add|keep|require|assert|check|fail|pin)\b[^.\n]{0,140}"
        r"(pytest\s+--collect-only|collect-only|collection (guard|check)|collected count)"
        r"|\bpytest\s+--collect-only\b",
        low,
    )
    unittest_shape = affirmed(
        r"\b(move|convert|wrap|make|place)\b[^.\n]{0,160}"
        r"(test_slugify_is_idempotent|hypothesis|property|function)[^.\n]{0,120}"
        r"(testcase|test case|method)"
        r"|\b(move|convert|wrap|make|place)\b[^.\n]{0,120}"
        r"(testcase|test case|method)[^.\n]{0,160}"
        r"(test_slugify_is_idempotent|hypothesis|property|function)",
        low,
    )
    unittest_runner = affirmed(
        r"\b(keep|retain|run|use)\b[^.\n]{0,120}"
        r"(python\s+-m\s+unittest\s+discover|unittest\s+discover)",
        low,
    )
    unittest_guard = affirmed(
        r"\b(add|keep|require|assert|check|verify|fail)\b[^.\n]{0,140}"
        r"(guard|test_slugify_is_idempotent|named test|test count|appears)",
        low,
    )
    python_remedy = (pytest_runner and pytest_guard) or (
        unittest_shape and unittest_runner and unittest_guard
    )
    if not python_diagnosis:
        errors.append("misses that unittest discovery does not collect the module-level Hypothesis test")
    if not python_remedy:
        errors.append("does not select a compatible runner and add an explicit exact-runner collection guard")

    go_replay = has(
        r"go test \./\.\..{0,180}(seed|corpus).{0,100}(replay|regression)"
        r"|(seed|corpus).{0,120}(replay|regression).{0,160}go test \./\.\.",
        low,
    ) and has(r"go test \./\.\..{0,100}(does not|doesn.t|not).{0,100}(active|discover|fuzz)", low)
    go_active = affirmed(
        r"\b(run|invoke|schedule|add|use)\b[^.\n]{0,180}"
        r"(-fuzz(?:=|\b)|active fuzz|fuzz discovery)",
        low,
    )
    go_semantics = go_replay and go_active
    go_inventory = (
        "fuzzdecodeframe" in low
        and "fuzzparseheader" in low
        and affirmed(
            r"\b(run|invoke|schedule|add|use|inventory)\b[^.]{0,180}"
            r"(each|both|matrix|one|two).{0,120}(-fuzz|invocation|target)",
            low,
        )
    )
    if not go_semantics:
        errors.append("does not distinguish Go seed replay from active -fuzz discovery")
    if not go_inventory:
        errors.append("does not inventory and actively schedule both Go fuzz targets")

    dead_diagnosis = has(
        r"normalizecandidate.{0,180}(copy|local|test.only|instead|not.{0,30}production|does not.{0,40}production)"
        r"|normalizecandidate.{0,120}(second|duplicate).{0,40}implementation"
        r"|(copy|local helper|test.only).{0,180}normalizeslug",
        low,
    )
    dead_remedy = affirmed(
        r"\b(import|call|exercise|route|point|target|test|invoke|use)\b.{0,140}"
        r"(production|normalizeslug)",
        low,
    ) or affirmed(
        r"\breplace\b[^.!?\n]{0,100}"
        r"(?:normalizecandidate|local (?:copied )?helper|copied (?:helper|implementation)|"
        r"(?:the )?copy\b)[^.!?\n]{0,100}\bwith\b[^.!?\n]{0,100}"
        r"(?:production|normalizeslug)",
        low,
    )
    retains_local_copy = affirmed(
        r"\b(retain|keep|continue(?:\s+to)?\s+use|use)\b[^.!?\n]{0,140}"
        r"(normalizecandidate|local (?:copied )?helper|copied (?:helper|implementation)|"
        r"(?:the )?copy\b)",
        low,
    ) or has(
        r"normalizeslug\s*\?\s*no\b"
        r"|\breplace\b[^.!?\n]{0,100}(?:production\s+)?normalizeslug"
        r"[^.!?\n]{0,100}\bwith\b[^.!?\n]{0,100}"
        r"(?:normalizecandidate|local (?:copied )?helper|copied (?:helper|implementation)|"
        r"(?:the )?copy\b)",
        low,
    )
    if not dead_diagnosis:
        errors.append("misses that the TypeScript property only tests normalizeCandidate, a local copy")
    if not dead_remedy:
        errors.append("does not route the property through the production normalizeSlug function")
    if retains_local_copy:
        errors.append("explicitly retains the test-local normalizeCandidate implementation")

    contradictions = [
        (r"\b(actively|automatically)\s+fuzz", r"go test \./\.\..{0,100}$", "claims the default Go command performs active fuzz discovery"),
        (r"\b(collect|run)\b.{0,80}hypothesis", r"unittest.{0,100}$", "claims unittest collects the Hypothesis function"),
        (r"\b(fine|safe|equivalent|acceptable)\b", r"(local|copied) (helper|implementation).{0,100}$", "accepts a test-local implementation as production coverage"),
    ]
    for claim, subject_before, message in contradictions:
        bad_claim = False
        for match in re.finditer(claim, low, re.IGNORECASE | re.DOTALL):
            before = low[max(0, match.start() - 140) : match.start()]
            if re.search(subject_before, before, re.IGNORECASE | re.DOTALL) and not negated_before(low, match.start()):
                bad_claim = True
                break
        if bad_claim:
            errors.append(message)

    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
