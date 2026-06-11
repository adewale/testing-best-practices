#!/usr/bin/env python3
from __future__ import annotations
import re, sys
from pathlib import Path

def read(root: Path, ext: str) -> str:
    return "\n".join(p.read_text(errors="ignore") for p in root.rglob(f"*.{ext}"))


def strip_comments_py(text: str) -> str:
    import re as _re
    text = _re.sub(r'(\"\"\".*?\"\"\")|(\'\'\'.*?\'\'\')', "", text, flags=_re.S)
    return "\n".join(line.split("#", 1)[0] for line in text.splitlines())

def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    text = read(root, "py"); low = text.lower()
    code = strip_comments_py(text).lower()
    errors = []
    if re.search(r"sleep\(\s*0?\.[0-9]|sleep\(\s*[1-9]", code):
        errors.append("real sleep still present; background transition was not made forceable")
    if not re.search(r"compact_now|\.compact\(\)|run_once|drain|process_pending|flush_now|\.flush\(\)|worker\s*=\s*false|auto_compact\s*=\s*false|start_worker\s*=\s*false|background\s*=\s*false|synchronous", low):
        errors.append("no forced-transition seam added to the system under test")
    if not re.search(r"pending|segment|count\(|len\(", low):
        errors.append("no assertion on observable pending/segment state")
    if low.count("assert") < 2:
        errors.append("too few assertions")
    for e in errors: print(e, file=sys.stderr)
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
