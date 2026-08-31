#!/usr/bin/env python3
"""E65 restraint oracle: a trusted, internally-constructed input does not earn a
fuzz harness just because the function formats a string."""
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


def read(root: Path, ext: str) -> str:
    return "\n".join(p.read_text(errors="ignore") for p in root.rglob(f"*.{ext}"))


def negated_before(text: str, start: int) -> bool:
    prefix = text[max(0, start - 140) : start]
    prefix = re.split(r"(?<=[.!?;:])\s+", prefix)[-1]
    return NEGATED.search(prefix) is not None


def affirmed(pattern: str, text: str) -> bool:
    return any(
        not negated_before(text, match.start())
        for match in re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
    )


def affirmed_predicate_after(subject: str, predicate: str, text: str, distance: int = 120) -> bool:
    for subject_match in re.finditer(subject, text, re.IGNORECASE | re.DOTALL):
        tail = text[subject_match.end() : subject_match.end() + distance]
        for predicate_match in re.finditer(predicate, tail, re.IGNORECASE | re.DOTALL):
            start = subject_match.end() + predicate_match.start()
            if not negated_before(text, start):
                return True
    return False


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    low = read(root, "md").lower()
    errors = []

    # Over-application: the fuzzing section names untrusted input as a trigger.
    # This input is package-internal and typed, so recommending a fuzz target is
    # the failure mode. Merely *mentioning* fuzzing to rule it out is fine.
    recommends_fuzz = affirmed(
        r"\b(add|write|create|introduce|run|schedule|augment|supplement|pair|combine)\b"
        r"[^.\n]{0,100}\b(?:fuzz|harness)"
        r"|\b(needs?|requires?|recommend\w*)\b[^.\n]{0,80}\bfuzz"
        r"|\bfunc fuzz\w*\("
        r"|\bgo test\s+-fuzz",
        low,
    ) or affirmed_predicate_after(
        r"\bfuzz (target|harness)\b",
        r"\b(needed|required|appropriate)\b",
        low,
    )
    # "Do not stop at examples; add a fuzz target" recommends fuzzing even
    # though the first clause contains a negation. Treat the contrastive action,
    # rather than the sentence-global "not", as the operative recommendation.
    recommends_fuzz = recommends_fuzz or re.search(
        r"\b(?:do not|don.t)\s+stop\b[^.!?\n]{0,180}"
        r"\b(?:add|write|create|introduce|run|schedule)\b[^.!?\n]{0,100}\bfuzz",
        low,
        re.IGNORECASE,
    ) is not None
    rules_fuzz_out = re.search(
        r"(no|not|don.?t|doesn.?t|isn.?t|without|unnecessary|unwarranted|"
        r"no need|not warranted|not required|skip)\b[^.\n]{0,40}\bfuzz"
        r"|fuzz\w*\b[^.\n]{0,40}(unnecessary|unwarranted|not warranted|not needed|"
        r"not required|overkill|would not|wouldn.?t|"
        r"not appropriate|inappropriate|"
        r"would add no (?:useful )?(?:signal|value|benefit)|"
        r"adds? (?:no|little) (?:useful )?(?:signal|value|benefit))",
        low,
    )
    if recommends_fuzz:
        errors.append(
            "over-applied fuzzing trigger: recommended a fuzz target for an "
            "internally-constructed, typed input that never crosses a trust boundary"
        )

    trusted_boundary = re.search(
        r"(internal|unexported|package).{0,160}(typed|schema|caller|trust|construct)"
        r"|(typed|schema|construct).{0,160}(internal|unexported|package|trust)"
        r"|does not cross.{0,80}(trust|request|file|process)",
        low,
        re.DOTALL,
    )
    if not trusted_boundary:
        errors.append("does not explain why this input stays inside a typed trust boundary")

    proportional_tier = re.search(
        r"table.?driven.{0,100}(right|appropriate|sufficient|proportional|keep)"
        r"|(right|appropriate|proportional).{0,100}table.?driven",
        low,
        re.DOTALL,
    ) and rules_fuzz_out
    if not proportional_tier:
        errors.append("does not choose table-driven examples and explicitly rule out fuzzing")
    if len(low.strip()) < 80:
        errors.append("empty assessment")

    for e in errors:
        print(e, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
