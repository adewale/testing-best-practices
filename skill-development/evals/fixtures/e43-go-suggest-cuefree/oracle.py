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
    if re.search(r"deepequal\(.{0,80}suggest", low, re.S):
        errors.append("pins exact results of an approximate search with DeepEqual")
    if "similarity(" not in low:
        errors.append("does not use the documented metric to build a reference")
    if not re.search(r"sort\.", text):
        errors.append("no exact reference ranking computed from the metric")
    if not re.search(r"[><]=?\s*0\.\d", text):
        errors.append("no fractional threshold assertion on the overlap")
    if not re.search(r"t\.(fatal|error)", low):
        errors.append("no assertions via testing.T")
    for e in errors: print(e, file=sys.stderr)
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
