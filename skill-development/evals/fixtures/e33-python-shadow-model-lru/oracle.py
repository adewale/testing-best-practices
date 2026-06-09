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
    if not re.search(r"random\.random\(|\.seed\(|random\(\s*\d", low):
        errors.append("no seeded RNG (fuzz must be reproducible)")
    if not ("for " in text and "range(" in text):
        errors.append("no randomized operation loop")
    if not (re.search(r"\bmodel\b|\bshadow\b|\bexpected\b", low) and low.count("assert") >= 3):
        errors.append("no parallel shadow model compared on each op")
    if not re.search(r"sorted\(|\.items\(\)|== model|deepequal", low):
        errors.append("no full-contents comparison (single observable only)")
    for e in errors: print(e, file=sys.stderr)
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
