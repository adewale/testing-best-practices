#!/usr/bin/env python3
from __future__ import annotations
import re
import sys
from pathlib import Path


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    files = list(root.rglob("*.test.ts")) + list(root.rglob("*.spec.ts")) + list(root.rglob("*.test.tsx"))
    text = "\n".join(p.read_text(errors="ignore") for p in files)
    low = text.lower()
    errors = []
    if "vitest" not in low and not re.search(r"\b(test|it)\s*\(", text):
        errors.append("missing Vitest-style test")
    if "javascript:" not in low:
        errors.append("missing dangerous javascript: URL case")
    if not any(safe in low for safe in ["https://", "http://", "mailto:", "/safe"]):
        errors.append("missing safe URL preservation case")
    if not re.search(r"\.not\.to(Be|Contain|Equal|Match|be|contain|equal|match)", text) and "toBeNull" not in text and "toEqual('')" not in text and 'toEqual("")' not in text and "toBe('')" not in text and 'toBe("")' not in text:
        errors.append("missing specific rejection/removal assertion")
    if not re.search(r"\.to(Contain|Equal|Be|contain|equal|be)\(", text):
        errors.append("missing positive preservation assertion")
    weak = len(re.findall(r"\bexpect\s*\(", text)) <= 2 and ("toBeDefined" in text or "toBeTruthy" in text)
    if weak:
        errors.append("weak truthy/defined-only oracle")
    if "console.log" in low or "print(" in low:
        errors.append("logging instead of assertion")
    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
