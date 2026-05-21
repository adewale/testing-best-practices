#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path

BAD = ["test.skip", "skip(", "retry", "run in order", "--runInBand", "sleep("]
GOOD = ["aftereach", "teardown", "cleanup", "reset", "t.cleanup", "monkeypatch", "restore", "finally"]
DIAG = ["global", "registry", "shared state", "order", "pollution", "environment", "env"]


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    text = "\n".join(p.read_text(errors="ignore") for p in root.rglob("*.*") if p.suffix in {".py", ".ts", ".tsx", ".go", ".rs", ".md"})
    low = text.lower()
    errors=[]
    for token in BAD:
        if token in low:
            errors.append(f"bad primary flake workaround: {token}")
    if not any(token in low for token in GOOD):
        errors.append("missing cleanup/reset/teardown fix")
    if not any(token in low for token in DIAG):
        errors.append("missing order/global-state diagnosis")
    if errors:
        for e in errors: print(e, file=sys.stderr)
        return 1
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
