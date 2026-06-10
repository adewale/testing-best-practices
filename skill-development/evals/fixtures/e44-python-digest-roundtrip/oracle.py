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
    if not ("json" in low and "binary" in low):
        errors.append("does not exercise both persistence formats")
    if not re.search(r"parametrize|for fmt|for format", low):
        errors.append("formats not parameterized/looped over a shared identity assertion")
    if not (re.search(r"random\(\s*\d+|\.seed\(", low) or re.search(r"range\(\s*[2-9]\d", text)):
        errors.append("no rich generated state (seeded RNG or wide generation loop)")
    if not re.search(r"sorted\(", text):
        errors.append("no canonicalization of unordered state before comparing")
    if not re.search(r"items\(", text):
        errors.append("no whole-state comparison via items()")
    if not ("ttl" in low and "set(" in low):
        errors.append("misses awkward value types (sets, TTLs)")
    for e in errors: print(e, file=sys.stderr)
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
