#!/usr/bin/env python3
from __future__ import annotations
import re
import sys
from pathlib import Path


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    text = "\n".join(p.read_text(errors="ignore") for p in root.rglob("*.rs"))
    low = text.lower()
    errors = []
    if "proptest" not in low:
        errors.append("missing proptest/property test")
    if re.search(r"parse_rule\([^\n;]+\)\.unwrap\(\)", text) or re.search(r"parse_rule\([^\n;]+\)\.expect\(", text):
        errors.append("unwraps arbitrary parse result")
    if "match parse_rule" not in low and "match parsed" not in low and ("ok(rule)" not in low or "err(err)" not in low):
        errors.append("missing Ok/Err branch assertions")
    if "span" not in low or "kind" not in low:
        errors.append("missing error kind/span assertions")
    if not re.search(r"prop_assert!?\s*\(", low) and "assert!(" not in low:
        errors.append("missing assertions")
    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
