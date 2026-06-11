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
    # Restraint: a trivial pure fn does not warrant a parallel model that
    # re-implements it. Flag a NON-test helper that rebuilds slugify (test
    # functions named test_slugify_* are fine), or explicit shadow/reference markers.
    reimpl = bool(re.search(r"def (?!test)\w*slug", low))  # non-test slugify-like helper
    if "shadow" in low or "reference_impl" in low or "reimplement" in low or reimpl:
        errors.append("built a redundant shadow-model reimplementation for a trivial pure function")
    if low.count("assert") < 2:
        errors.append("too few direct assertions")
    for e in errors: print(e, file=sys.stderr)
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
