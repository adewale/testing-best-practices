#!/usr/bin/env python3
"""Oracle for E72: fidelity expectations must come from the real service.

The test is named `changes_0` but asserts `changes == 1` for a DELETE that matches
nothing, and production code relies on `changes == 0`. Passing shape: flags that the
expected value is unverified/wrong (SQLite/D1 report 0 rows changed for a no-match
DELETE) and recommends deriving it from the real engine (sqlite3, local D1 via
wrangler/miniflare, or a recording). Failing shapes: endorses the mock, or proposes
changing production to expect 1.
"""
from __future__ import annotations
import re, sys
from pathlib import Path

NEG = re.compile(r"(\bnot\b|n't|\bno\b|\bnever\b)[^.\n]{0,20}$")

def unnegated(pattern: str, text: str) -> bool:
    for m in re.finditer(pattern, text):
        if not NEG.search(text[max(0, m.start() - 40):m.start()]):
            return True
    return False

def main() -> int:
    low = "\n".join(p.read_text(errors="ignore") for p in Path(sys.argv[1]).rglob("*.md")).lower()
    low = re.sub(r"\s+", " ", low)
    errors = []
    flags = re.search(r"(changes\s*==\s*1|changes of 1|returns 1|reports 1)[^\n]{0,240}(wrong|incorrect|contradict|unverified|belief|should be 0|0 rows|zero rows|would be 0|is 0)", low) or \
            re.search(r"(no[- ]match|matches nothing|matched nothing|no rows|zero rows)[^\n]{0,240}(changes\s*(==|of|=)\s*0|0 changes|zero changes|report 0|returns 0|is 0)", low)
    if not flags:
        errors.append("does not flag that `changes == 1` for a no-match DELETE is an unverified/wrong expectation")
    if not re.search(r"sqlite|local d1|wrangler d1|miniflare|record|real d1|real service|real engine|emulat", low):
        errors.append("does not say where the expected value should come from (real engine or recording)")
    if unnegated(r"(mockd1|the mock) is (faithful|accurate|correct)", low) or unnegated(r"test (correctly|properly) verifies", low):
        errors.append("endorses the mock as faithful")
    if re.search(r"(change|update)[^.\n]{0,40}routes\.py[^.\n]{0,80}changes\s*==\s*1", low):
        errors.append("proposes bending production to the mock (expect changes == 1)")
    for e in errors:
        print(e, file=sys.stderr)
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
