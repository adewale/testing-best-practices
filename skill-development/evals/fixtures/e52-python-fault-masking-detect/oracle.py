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
    if not re.search(r"clamp|max\(|min\(|except|swallow|mask|default", low):
        errors.append("does not identify the fault-masking constructs")
    if not re.search(r"(still|would|will) pass|passes (even|regardless)|can.?t catch|cannot catch|won.?t catch|hides? (the )?fault|"
                     r"(not |never )?propagat|broken.{0,40}(pass|undetect)|weak evidence|even if .* (broken|crash)|infect|"
                     r"tautolog|structurally (enforce|guarant)|cannot distinguish|always (return|satisf)|illusion", low):
        errors.append("does not explain the test passes even when the computation is broken")
    if not re.search(r"assert.{0,40}(specific|exact|expected|internal|pre.?clamp|before)|test.{0,20}(directly|heavy_calc|calc\()|"
                     r"let it (raise|fail|propagate)|remove the.{0,20}except|surface|mutation", low):
        errors.append("does not recommend asserting pre-mask/exact state or surfacing the error")
    for e in errors: print(e, file=sys.stderr)
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
