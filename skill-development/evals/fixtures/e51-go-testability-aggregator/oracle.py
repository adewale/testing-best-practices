#!/usr/bin/env python3
from __future__ import annotations
import re, sys
from pathlib import Path

def read(root: Path, ext: str) -> str:
    return "\n".join(p.read_text(errors="ignore") for p in root.rglob(f"*.{ext}"))


def strip_comments_go(text: str) -> str:
    import re as _re
    text = _re.sub(r"/\*.*?\*/", "", text, flags=_re.S)
    return "\n".join(line.split("//", 1)[0] for line in text.splitlines())

def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    text = read(root, "go"); low = text.lower()
    code = strip_comments_go(text).lower()
    errors = []
    if re.search(r"time\.sleep\(", code):
        errors.append("real sleep still present; background transition was not made forceable")
    if not re.search(r"drain|flushnow|flush\(|runonce|process\(|synchronous|nowait|sync mode|startworker|noworker|worker\s*:\s*false", low):
        errors.append("no forced-drain seam added to the system under test")
    if not re.search(r"total\(|pending|len\(", low):
        errors.append("no assertion on observable aggregate/pending state")
    if not re.search(r"t\.(fatal|error)", low):
        errors.append("no assertions via testing.T")
    for e in errors: print(e, file=sys.stderr)
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
