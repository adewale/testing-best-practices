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
    if re.search(r"sleep\(\s*[1-9]", low):
        errors.append("long real sleep still present; transition was not made forceable")
    if not re.search(r"flush_now|force_flush|\.flush\(\)|run_once|drain\(|auto_flush\s*=\s*false|start\s*=\s*false|no_thread|background\s*=\s*false", low):
        errors.append("no forced-transition seam added to the system under test")
    if not re.search(r"pending|read|contents|getvalue|records", low):
        errors.append("no assertion on observable persisted/pending state")
    if low.count("assert") < 2:
        errors.append("too few assertions")
    for e in errors: print(e, file=sys.stderr)
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
