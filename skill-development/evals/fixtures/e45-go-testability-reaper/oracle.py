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
    if re.search(r"time\.sleep\(\s*\d+\s*\*\s*time\.(second|minute)", low):
        errors.append("multi-second real sleep still present; transition was not made forceable")
    if not re.search(r"reapnow|reaponce|runonce|sweep|reap\(\)|noreaper|startreaper|clock|nowfunc|now func", low):
        errors.append("no forced-transition seam added to the system under test")
    if not re.search(r"idlecount|idle\(|len\(|count\(|size\(", low):
        errors.append("no assertion on observable pool state")
    if not re.search(r"t\.(fatal|error)", low):
        errors.append("no assertions via testing.T")
    for e in errors: print(e, file=sys.stderr)
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
