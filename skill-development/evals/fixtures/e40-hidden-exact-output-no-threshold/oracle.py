#!/usr/bin/env python3
from __future__ import annotations
import re, sys
from pathlib import Path

def read(root: Path, ext: str) -> str:
    return "\n".join(p.read_text(errors="ignore") for p in root.rglob(f"*.{ext}"))

def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    text = read(root, "py"); low = text.lower()
    errors = []
    # Restraint: a deterministic sort must be asserted exactly, NOT statistically.
    over = re.search(r"recall|approx|tolerance|assertalmostequal|>=\s*0\.\d|abs\([^)]*\)\s*<", low)
    if over:
        errors.append("over-applied a statistical/closeness oracle to a deterministic, exact output")
    if not re.search(r"==\s*sorted\(|==\s*\[|==\s*expected", low):
        errors.append("no exact-equality assertion on the sorted output")
    for e in errors: print(e, file=sys.stderr)
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
