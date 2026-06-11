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
        errors.append("no seeded RNG (fuzz must be reproducible)")
    if not re.search(r"for .*\{", text):
        errors.append("no randomized operation loop")
    if not re.search(r"\bmodel\b|\bshadow\b|\bexpected\b", low):
        errors.append("no parallel shadow model")
    if not re.search(r"t\.(fatal|error|fatalf|errorf)", low):
        errors.append("no assertions via testing.T")
    if not re.search(r"deepequal|reflect\.|len\(", low):
        errors.append("no contents comparison (single observable only)")
    for e in errors: print(e, file=sys.stderr)
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
