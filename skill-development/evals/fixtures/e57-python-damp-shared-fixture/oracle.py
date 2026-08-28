#!/usr/bin/env python3
"""Oracle for E57: the assessment must catch test logic that mirrors the
implementation and the mutated shared fixture that separates cause from
effect — and must not "fix" the file by pushing even more setup into shared
helpers/fixtures.

Passing shape:
  1. Flags the loop/branch/computed expectation inside the test (the
     `balance * 0.1` expectation re-derives the documented rule, so it can
     share a bug with the implementation).
  2. Flags the shared mutable module state / setUpClass mutation far from the
     assertion (cause-effect distance, cross-test coupling).
  3. Recommends splitting into explicit per-behavior tests with local,
     literal data — not consolidating further into shared fixtures.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def read(root: Path, ext: str) -> str:
    return "\n".join(p.read_text(errors="ignore") for p in root.rglob(f"*.{ext}"))


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    text = read(root, "md")
    low = text.lower()
    errors: list[str] = []
    if not low.strip():
        print("no markdown assessment found", file=sys.stderr)
        return 1

    flags_logic = re.search(
        r"logic in (the )?tests?|loop|conditional|if/else|branch(es|ing)? in (the )?test"
        r"|computed expect|derives? the expect|re-?deriv|mirrors? the (implementation|rule)"
        r"|same (formula|calculation|logic) as",
        low,
    )
    if not flags_logic:
        errors.append("does not flag the loop/branch/computed expectation inside the test")

    flags_fixture = re.search(
        r"shared (mutable |module |global )?(state|fixture|data)|global (state|list|variable)"
        r"|module-?level|setupclass|mutat\w+ (the )?(fixture|accounts|state)"
        r"|cause and effect|far from the assert|action at a distance|cross-test coupling"
        r"|test (order|pollution|interdependence)",
        low,
    )
    if not flags_fixture:
        errors.append(
            "does not flag the shared mutable fixture / setUpClass mutation "
            "(cause-effect distance)"
        )

    recommends_split = re.search(
        r"split|separate tests?|one test per|per[- ]behavior|individual tests?"
        r"|inline (the )?(setup|data)|local(ly)? (defined|constructed)? ?(setup|data)"
        r"|literal (value|expected|data)|explicit (data|setup|values)",
        low,
    )
    if not recommends_split:
        errors.append("does not recommend per-behavior tests with local, explicit data")

    over_dry = re.search(
        r"(move|extract|consolidate|centraliz\w+|pull)\w* [^.\n]{0,60}"
        r"(into|to) (a |an |one )?(shared|common|central|reusable) "
        r"(fixture|helper|setup|base ?class)",
        low,
    )
    if over_dry:
        errors.append(
            "recommends consolidating even more setup into shared fixtures/helpers "
            "(the DRY-harder over-application)"
        )

    for e in errors:
        print(e, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
