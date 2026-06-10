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
    if re.search(r"\.search\([^)]*\)\s*==\s*\[", text):
        errors.append("pins an exact result list for an approximate search")
    if "similarity(" not in low:
        errors.append("does not use the documented metric to build a reference")
    if not re.search(r"sorted\(.{0,120}similarity|similarity.{0,120}sorted\(", low, re.S):
        errors.append("no exact reference ranking computed from the metric")
    if not re.search(r"&|\.intersection\(", text):
        errors.append("no overlap computed between approximate and reference results")
    if not re.search(r"[><]=\s*(0\.\d+|\d)", text):
        errors.append("no threshold assertion on the overlap")
    if re.search(r"\brandom\b", low) and not re.search(r"random\(\s*\d+|\.seed\(", low):
        errors.append("unseeded randomness in an approximate-output test")
    for e in errors: print(e, file=sys.stderr)
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
