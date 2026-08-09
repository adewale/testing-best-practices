#!/usr/bin/env python3
"""E56 oracle: does the assessment notice the tests that never run?

Two defects are planted and both are invisible to a test count:
  1. include: ['src/**/*.test.ts'] does not collect test/staging/, so 31
     payment-failure tests have never run.
  2. the e2e job is continue-on-error, so 18 Playwright tests cannot fail CI.

Passing shape: name at least the collection gap, name the advisory lane, and do
not conclude the suite is healthy. Matching is over prose with code blocks
removed so a quoted config snippet is not mistaken for the finding.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def read(root: Path) -> str:
    return "\n".join(p.read_text(errors="ignore") for p in root.rglob("*.md"))


def normalise(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"[*_]+", "", text)
    return text.lower()


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    raw = read(root)
    low = normalise(raw)
    errors: list[str] = []

    # 1. The collection gap. Prose OR the concrete verification command counts.
    collection = re.search(
        r"never (?:runs|ran|been run|collected)|not (?:be )?collect|"
        r"does not collect|excluded? (?:by|from) the (?:glob|include)|"
        r"outside (?:the )?(?:glob|include|src)|not (?:part of|among) the 210|"
        r"cannot fail|do(?:es)? not run",
        low,
    ) or re.search(r"vitest list|--collect-only|collected[- ]vs|on disk", low)
    if not collection:
        errors.append("missed the collection gap: test/staging is outside the include glob")

    # 2. The advisory lane.
    advisory = re.search(r"continue-on-error|advisory|cannot fail the build|"
                         r"can(?:'|no)?t break the build|non-?blocking|not gating", low)
    if not advisory:
        errors.append("missed that the e2e job is continue-on-error and cannot fail the build")

    # 3. Must not sign off. A clean bill of health is the failure this probe catches.
    healthy = re.search(
        r"(?:suite|coverage|this) (?:looks|is|seems) (?:healthy|good|solid|thorough|fine)|"
        r"ready to ship|good sign|thorough coverage|no (?:major )?(?:issues|concerns)",
        low,
    )
    if healthy and not collection:
        errors.append("signed the suite off as healthy")
    elif healthy and not advisory:
        errors.append("signed the suite off as healthy despite the advisory lane")

    if len(low.split()) < 40:
        errors.append("empty assessment")

    for e in errors:
        print(e, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
