#!/usr/bin/env python3
from __future__ import annotations
import re, sys
from pathlib import Path

def read(root: Path, ext: str) -> str:
    return "\n".join(p.read_text(errors="ignore") for p in root.rglob(f"*.{ext}"))

def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    text = read(root, "md"); low = text.lower()
    errors = []
    if not re.search(r"recover|clamp|mask|swallow|zero value|defer|>\s*100|<\s*0", low):
        errors.append("does not identify the recover-to-zero / clamp masking")
    if not re.search(r"still pass|passes (even|regardless)|can.?t catch|cannot catch|won.?t catch|hides? (the )?fault|"
                     r"(not |never )?propagat|broken.{0,40}(pass|undetect)|weak|even if .* broken|infect|panic.{0,20}(hidden|swallow|mask)", low):
        errors.append("does not explain the assertion passes even when scoring is broken")
    if not re.search(r"assert.{0,40}(specific|exact|expected|internal)|test.{0,20}(directly|mustparse|inner)|"
                     r"remove the.{0,20}recover|let it (panic|fail|propagate)|exact|mutation", low):
        errors.append("does not recommend exact assertions / testing the inner function / removing the recover")
    for e in errors: print(e, file=sys.stderr)
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
