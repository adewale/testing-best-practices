#!/usr/bin/env python3
from __future__ import annotations
import re, sys
from pathlib import Path

def read(root: Path, ext: str) -> str:
    return "\n".join(p.read_text(errors="ignore") for p in root.rglob(f"*.{ext}"))

def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    text = read(root, "go"); low = text.lower()
    errors = []
    if not re.search(r"newsource\(|rand\.seed\(", low):
        errors.append("no seeded RNG (approximate must not mean flaky)")
    if not re.search(r"brute|linear|exacttopk|reference", low):
        errors.append("no brute-force/linear oracle")
    if "recall" not in low:
        errors.append("no recall metric against the oracle")
    if not re.search(r"recall\s*[<>]=?\s*0?\.\d|>=\s*0\.[5-9]|<\s*0\.[5-9]", low):
        errors.append("no recall threshold with margin")
    for e in errors: print(e, file=sys.stderr)
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
