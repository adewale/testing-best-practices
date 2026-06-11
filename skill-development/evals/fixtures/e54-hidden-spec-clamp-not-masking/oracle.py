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
    # Restraint: the clamp IS the documented behavior under test. Flagging it as
    # fault-masking and recommending its removal is the over-application failure.
    flags_masking = re.search(r"fault.?mask|asserting through|hides? (a |the )?fault|anti.?pattern", low)
    says_remove = re.search(r"remove the.{0,15}clamp|don.?t clamp|should (raise|not clamp)|let .* raise|surface the (fault|error)|stop clamping", low)
    if flags_masking and says_remove:
        errors.append("over-applied fault-masking: flagged the documented clamp as a smell AND recommended removing it")
    if not re.search(r"clamp|contract|document|spec> ?ied|specified|behavior|\[0, ?100\]|range", low):
        errors.append("does not engage with the clamp/contract at all")
    if low.count("assert") < 1 and "clamp" not in low:
        errors.append("empty assessment")
    for e in errors: print(e, file=sys.stderr)
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
