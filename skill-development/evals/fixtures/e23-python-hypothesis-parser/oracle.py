#!/usr/bin/env python3
from __future__ import annotations
import re
import sys
from pathlib import Path


def read_py(root: Path) -> str:
    return "\n".join(p.read_text(errors="ignore") for p in root.rglob("*.py"))


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    text = read_py(root)
    low = text.lower()
    errors = []
    if "hypothesis" not in low or "@given" not in text:
        errors.append("missing Hypothesis @given property")
    if not re.search(r"parse\w*\(", text):
        errors.append("missing parser call")
    if "parseerror" not in low:
        errors.append("missing structured ParseError assertions")
    if "config" not in low:
        errors.append("missing Config invariants")
    if re.search(r"assert\s+\w+\s+is\s+not\s+none", low) and len(re.findall(r"assert\s+", low)) <= 2:
        errors.append("weak not-None-only assertion")
    if re.search(r"except\s+exception\s*:\s*(pass|return)", low):
        errors.append("swallows arbitrary exceptions")
    if not re.search(r"assert\s+.*(kind|span|message|name|settings|value|len\()", low):
        errors.append("missing meaningful field/invariant assertion")
    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
