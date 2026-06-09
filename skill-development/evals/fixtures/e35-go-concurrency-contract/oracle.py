#!/usr/bin/env python3
"""Oracle for E35: concurrent tests must pin the concurrency contract.

A passing suite (1) exercises the shared state from concurrent goroutines with
real synchronization, and (2) ASSERTS the promised invariant -- here,
compute-at-most-once -- with a failing-capable check *inside the concurrent
test*, rather than only logging the observed count (the classic "I saw the race
and t.Logf'd it" mistake). Asserting compute-once only in a sequential test does
not count: the contract must be pinned under contention.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ASSERT_MSG = re.compile(r"t\.(Errorf?|Fatalf?)\([^)]*comput", re.IGNORECASE)
ASSERT_CMP = re.compile(r"comput\w*call\w*[\w.()\s]*(==|!=|>)\s*\d", re.IGNORECASE)


def func_chunks(text: str) -> list[str]:
    """Split Go source into top-level func bodies (good-enough brace matching)."""
    chunks = []
    for m in re.finditer(r"\bfunc\b", text):
        start = text.find("{", m.start())
        if start == -1:
            continue
        depth, i = 0, start
        while i < len(text):
            depth += (text[i] == "{") - (text[i] == "}")
            if depth == 0:
                chunks.append(text[m.start():i + 1])
                break
            i += 1
    return chunks


def asserts_compute_count(chunk: str) -> bool:
    return bool(ASSERT_MSG.search(chunk) or ASSERT_CMP.search(chunk))


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    text = "\n".join(p.read_text(errors="ignore") for p in root.rglob("*.go"))
    low = text.lower()
    errors: list[str] = []

    if "go func" not in low:
        errors.append("no concurrent goroutines exercised (`go func`)")
    if not any(s in low for s in ("waitgroup", "errgroup", "sync.wait")):
        errors.append("no goroutine synchronization (WaitGroup/errgroup)")

    # The compute-at-most-once invariant must be asserted *within a concurrent
    # test function*, not only in a sequential one (and not merely logged).
    concurrent_funcs = [c for c in func_chunks(text) if "go func" in c]
    if concurrent_funcs and not any(asserts_compute_count(c) for c in concurrent_funcs):
        errors.append(
            "concurrent test does not assert compute-at-most-once (only logs the "
            "observed count or asserts it sequentially); the contention contract "
            "is not pinned, so the double-compute race is tolerated"
        )

    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

