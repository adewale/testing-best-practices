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
    # False-failure trap: hashing or string-comparing a dump whose order varies.
    if re.search(r"hashlib|sha256|md5", low) and "sorted(" not in low:
        errors.append("digests a nondeterministic dump without canonicalizing (sorting) first")
    if re.search(r"(str|repr)\(\s*\w*\.?neighbors\(", low):
        errors.append("compares the textual form of an unordered set")
    if re.search(r"list\(\s*\w*\.?neighbors\([^)]*\)\s*\)\s*==\s*\[", text) and "sorted(" not in low:
        errors.append("asserts neighbor list order, which is unspecified")
    if "neighbors(" not in low:
        errors.append("does not compare neighbor sets at all")
    if not re.search(r"sorted\(|==\s*\{|set\(|==\s*\w+\.neighbors\(", text):
        errors.append("no structural or canonicalized comparison of the graph")
    if low.count("assert") < 2:
        errors.append("too few assertions")
    for e in errors: print(e, file=sys.stderr)
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
