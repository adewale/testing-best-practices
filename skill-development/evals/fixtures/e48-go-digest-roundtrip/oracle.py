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
    if not ("formatjson" in low and "formatgob" in low):
        errors.append("does not exercise both persistence formats")
    if not re.search(r"newsource\(|rand\.seed\(|for i := 0; i < [2-9]\d", low):
        errors.append("no rich generated state (seeded RNG or wide generation loop)")
    if not re.search(r"deepequal\(|canonical", low):
        errors.append("no whole-state structural comparison")
    if "snapshot(" not in low:
        errors.append("does not compare the full snapshot")
    if "ttl" not in low:
        errors.append("misses TTL coverage")
    if not re.search(r"t\.(fatal|error)", low):
        errors.append("no assertions via testing.T")
    for e in errors: print(e, file=sys.stderr)
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
