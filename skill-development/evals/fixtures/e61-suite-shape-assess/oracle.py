#!/usr/bin/env python3
"""Oracle for E61: the assessment must diagnose the suite's *shape*, not just
individual tests.

Passing shape:
  1. Names the distribution problem (inverted pyramid / ice-cream cone /
     top-heavy E2E vs. a thin unit base) rather than only the flakiness.
  2. Calls out the missing integration middle.
  3. Recommends moving specific coverage down-tier (business rules like VAT/
     coupon/rounding out of the browser and into unit/domain tests).
  4. Keeps a small E2E core (golden path / critical journeys) rather than
     deleting E2E outright.

Over-application/failure shapes: prescribing more E2E coverage, or fixing the
red releases with more retries/longer timeouts.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def read(root: Path, ext: str) -> str:
    return "\n".join(p.read_text(errors="ignore") for p in root.rglob(f"*.{ext}"))


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    low = read(root, "md").lower()
    errors: list[str] = []
    if not low.strip():
        print("no markdown assessment found", file=sys.stderr)
        return 1

    if not re.search(
        r"pyramid|ice[- ]?cream|inverted|top[- ]?heavy|upside[- ]?down"
        r"|(shape|distribution|balance|ratio) of (the )?(suite|tests)"
        r"|suite('s)? (shape|distribution|balance)|38 e2e .{0,30}(vs|versus|against|to) .{0,10}4",
        low,
    ):
        errors.append("does not diagnose the suite's shape/distribution (38 E2E vs 4 unit)")

    if "integration" not in low:
        errors.append("does not mention the missing integration tier")

    if not re.search(
        r"(move|push|convert|migrat\w+|extract|rewrite|reimplement|cover)\w*[^.\n]{0,90}"
        r"(unit|integration|domain|service)[- ]?(level|layer|test|tier|seam)?"
        r"|test\w* [^.\n]{0,40}(vat|coupon|rounding|business rule)[^.\n]{0,60}"
        r"(without|below|outside) the (browser|ui)",
        low,
    ):
        errors.append(
            "does not recommend moving business-rule coverage down-tier "
            "(VAT/coupon/rounding out of the browser)"
        )

    if not re.search(
        r"(keep|retain|reduce to|small (set|number|core)|handful|golden path"
        r"|critical (user )?journe|a few) [^.\n]{0,60}(e2e|end[- ]to[- ]end|selenium)"
        r"|(e2e|end[- ]to[- ]end)[^.\n]{0,60}(golden path|critical (user )?journe|handful|small (set|core|number))"
        r"|critical[- ](user[- ]|path[- ]?)?journe"
        r"|(small (set|number|core)|handful|a few)[^.\n]{0,60}journe",
        low,
    ):
        errors.append("does not keep a small E2E core (golden path / critical journeys)")

    # Doubling-down recommendations fail — but an assessment may *name* these
    # moves in order to reject them ("adding more e2e ... is the wrong one"),
    # so a match followed closely by negation language does not count
    # (validated against a real model candidate with a what-not-to-do list).
    doubling = re.compile(
        r"(add\w*|write|increase|more)[^.\n]{0,30}(retr(y|ies))"
        r"|(raise|increase|bump|longer)[^.\n]{0,25}timeout"
        r"|(add\w*|write)[^.\n]{0,30}more (e2e|end[- ]to[- ]end|selenium)"
    )
    negated = re.compile(
        r"wrong|avoid|don'?t|do not|trap|mistake|anti[- ]?pattern|worse"
        r"|not the (answer|fix|move)|resist|instead of|rather than|stop"
    )
    for m in doubling.finditer(low):
        window = low[max(0, m.start() - 120): m.end() + 160]
        if not negated.search(window):
            errors.append(
                "recommends more retries/timeouts/E2E — doubling down on the ice-cream cone"
            )
            break

    for e in errors:
        print(e, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
