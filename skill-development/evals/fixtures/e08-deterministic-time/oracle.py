#!/usr/bin/env python3
from __future__ import annotations
import re
import sys
from pathlib import Path

BAD = ["sleep(", "time.sleep", "Thread.Sleep", "Task.Delay", "waitForTimeout", "setTimeout(", "skip(", "test.skip"]
GOOD = ["fakeclock", "fake_clock", "clock", "scheduler", "advance", "tick", "run_pending", "wait_until"]


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    text = "\n".join(p.read_text(errors="ignore") for p in root.rglob("*.*") if p.suffix in {".py", ".ts", ".tsx", ".go", ".rs", ".md"})
    # Mentions like "do not use sleep" are acceptable in prose. Forbid only
    # actual sleep/timeout calls in candidate code or unqualified recommendations.
    low = "\n".join(
        line.lower() for line in text.splitlines()
        if not any(guard in line.lower() for guard in ["do not", "don't", "never", "instead of", "without", "using `sleep", "using sleep", "fixed `sleep", "fixed sleep", "replace"])
    )
    errors=[]
    for token in BAD:
        if token.lower() in low:
            errors.append(f"forbidden flake token: {token}")
    if not any(token in low for token in GOOD):
        errors.append("missing fake/injected clock or deterministic scheduler signal")
    if not re.search(r"assert|expect\(|require\.|t\.fatal|prop_assert", low):
        errors.append("missing assertion")
    if errors:
        for e in errors: print(e, file=sys.stderr)
        return 1
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
