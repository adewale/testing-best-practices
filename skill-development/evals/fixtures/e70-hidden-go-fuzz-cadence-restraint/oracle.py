#!/usr/bin/env python3
"""E70 restraint oracle: preserve a proportional, fully inventoried fuzz cadence."""
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


def prohibits(pattern: str, text: str) -> bool:
    return re.search(
        r"\b(?:do not|don.t|should not|must not|never)\b[^.\n]{0,60}" + pattern,
        text,
        re.IGNORECASE | re.DOTALL,
    ) is not None


def affirmed_predicate_after(subject: str, predicate: str, text: str, distance: int = 180) -> bool:
    for subject_match in re.finditer(subject, text, re.IGNORECASE | re.DOTALL):
        tail = text[subject_match.end() : subject_match.end() + distance]
        for predicate_match in re.finditer(predicate, tail, re.IGNORECASE | re.DOTALL):
            start = subject_match.end() + predicate_match.start()
            if not negated_before(text, start):
                return True
    return False


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    low = read_markdown(root).lower()
    errors: list[str] = []
    if not low.strip():
        print("no markdown assessment found", file=sys.stderr)
        return 1

    replay_semantics = has(
        r"go test \./\.\..{0,180}(seed|corpus).{0,100}(replay|regression)"
        r"|go test \./\.\..{0,140}replays?.{0,80}(seed|corpus)"
        r"|(seed|corpus).{0,120}(replay|regression).{0,160}go test \./\.\.",
        low,
    )
    active_semantics = affirmed(
        r"\b(run|runs|invoke|invokes|perform|performs|schedule|schedules|do|does)\b.{0,180}"
        r"(-fuzz|active (fuzz|discovery)|coverage-guided (mutation|fuzz))"
        r"|\b(matrix|job)\b.{0,100}\b(does|performs|runs)\b.{0,100}active.{0,100}-fuzz"
        r"|\b(active|coverage-guided)\b.{0,100}(discover|mutation|fuzz).{0,160}"
        r"(-fuzz|matrix|pr job|scheduled job)",
        low,
    )
    semantics = replay_semantics and active_semantics
    if not semantics:
        errors.append("does not distinguish go test seed replay from explicit active fuzz discovery")

    names_or_complete_matrix = (
        ("fuzzdecodeframe" in low and "fuzzparseheader" in low)
        or has(r"both.{0,60}(discover|inventory|fuzz).{0,80}target.{0,120}(both|two|workflow|matrix)", low)
    )
    one_per_invocation = affirmed(
        r"\b(run|runs|invoke|invokes|keep|keeps|use|uses|schedule|schedules|verify|verifies)\b.{0,160}"
        r"(one.{0,50}target.{0,60}(per|each).{0,50}(invocation|process)"
        r"|separate invocation|exact target regex)",
        low,
    )
    inventory = names_or_complete_matrix and one_per_invocation
    if not inventory:
        errors.append("does not verify complete two-target inventory and one-target-per-invocation execution")

    cadence_shape = has(
        r"(bounded|short|20.?s|smoke).{0,160}(pr|pull request).{0,200}"
        r"(scheduled|nightly|daily|20.?m|long)"
        r"|(pr|pull request).{0,160}(bounded|short|20.?s|smoke).{0,200}"
        r"(scheduled|nightly|daily|20.?m|long)",
        low,
    )
    cadence_endorsement = affirmed(
        r"\b(keep|retain|endorse|preserve)\b.{0,180}(cadence|pr|smoke|scheduled|campaign)"
        r"|\b(appropriate|proportional|sound|sensible|reasonable|balanced|"
        r"right cadence|good cadence)\b",
        low,
    ) or prohibits(
        r"\b(remove|drop|replace|delete|retire|disable|eliminate|cancel)\b"
        r".{0,100}(scheduled|nightly|daily)",
        low,
    ) or re.search(
        r"\bno\b[^.!?\n]{0,80}(?:duration|workflow|cadence|schedule)"
        r"[^.!?\n]{0,60}(?:change|changes)[^.!?\n]{0,40}"
        r"(?:needed|required|warranted)",
        low,
        re.IGNORECASE,
    ) is not None
    rejects_cadence = re.search(
        r"\b(?:keep|retain|preserve)\s+none\b[^.!?\n]{0,140}"
        r"(?:cadence|workflow|schedule|campaign|pr|replay)"
        r"|\b(?:scheduled|nightly|daily)\s+(?:fuzz\s+)?(?:workflow|campaign|job)"
        r"\s+(?:should|must|needs? to)\s+(?:go|be\s+(?:removed|dropped|deleted))",
        low,
        re.IGNORECASE,
    ) or affirmed_predicate_after(
        r"\b(?:scheduled|nightly|daily)\s+(?:fuzz\s+)?(?:workflow|campaign|job)\b",
        r"\bredundant\b",
        low,
    )
    cadence = cadence_shape and cadence_endorsement
    if not cadence:
        errors.append("does not recognize the bounded-PR plus longer-scheduled cadence as proportional")

    corpus = affirmed(
        r"\b(commit|promote|preserve|upload|retain|attach)\w*\b.{0,180}"
        r"(artifact|minimized|failing input|crasher|failure|input).{0,140}(corpus|testdata/fuzz|replay|issue)"
        r"|\b(commit|promote)\w*\b.{0,120}(failure|input|crasher).{0,100}"
        r"(corpus|testdata/fuzz)",
        low,
    )
    if not corpus:
        errors.append("does not preserve artifacts and promote minimized failures into the regression corpus")

    if affirmed_predicate_after(
        r"go test \./\.\.", r"\b(actively|automatically)\s+fuzz", low
    ):
        errors.append("claims the default test command performs active fuzz discovery")
    if affirmed(
        r"\b(change|increase|raise|run)\b.{0,100}"
        r"(?:30\s*(?:minutes?|m)\b|half[- ]?hour|hour|20m)"
        r".{0,140}(?:every|each).{0,30}(?:pr|pull request)"
        r"|\b(?:every|each)\s+(?:pr|pull request)\b[^.!?\n]{0,140}"
        r"(?:30\s*(?:minutes?|m)\b|half[- ]?hour|hour[- ]long|20m)",
        low,
    ):
        errors.append("demands a long discovery campaign on every pull request")
    if affirmed(
        r"\b(remove|drop|replace|delete|retire|disable|eliminate|cancel)\b"
        r".{0,100}(scheduled|nightly|daily).{0,100}(fuzz|campaign|workflow|job)",
        low,
    ):
        errors.append("removes the scheduled discovery campaign")
    if rejects_cadence:
        errors.append("rejects the proportional PR/scheduled campaign cadence")
    if affirmed(r"\b(remove|skip|drop)\b.{0,80}go test \./\.\.", low):
        errors.append("removes default seed-corpus regression replay")
    if affirmed(r"\bonly\b.{0,50}fuzzdecodeframe.{0,80}(run|active|matrix|scheduled)", low):
        errors.append("incorrectly reports that only one fuzz target is scheduled")

    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
