#!/usr/bin/env python3
from __future__ import annotations
import re
import sys
from pathlib import Path


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    text = "\n".join(p.read_text(errors="ignore") for p in root.rglob("*.*") if p.suffix in {".go", ".md", ".txt"})
    low = text.lower()
    errors=[]
    if "zero value" not in low and "var e email" not in low:
        errors.append("missing Go zero-value caveat")
    if "unconstructible" in low and not any(term in low for term in ["not", "isn't", "is not", "still", "zero value"]):
        errors.append("claims invalid Email is simply unconstructible")
    if re.search(r"email\{\}.*outside.*compiles", low):
        errors.append("uses false outside-package Email{} compiles claim")
    if "email{}" in low and "zero value" in low and not any(term in low for term in ["outside", "compiles"]):
        # Email{} is a legitimate shorthand for the zero value when not used as
        # the false outside-package composite-literal claim.
        pass
    risky_delete_lines = [
        line for line in low.splitlines()
        if ("delete all" in line or "delete every" in line)
        and not any(guard in line for guard in ["do not", "don't", "not", "only"])
    ]
    if risky_delete_lines:
        errors.append("unsafe blanket deletion of invalid-email tests")
    if not any(term in low for term in ["constructor", "newemail", "parseemail", "boundary"]):
        errors.append("missing constructor/boundary test preservation")
    if errors:
        for e in errors: print(e, file=sys.stderr)
        return 1
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
