#!/usr/bin/env python3
from __future__ import annotations
import re
import sys
from pathlib import Path

BAD_IMPORTS = ["net/http", "http.NewRequest", "smtp.", "os.TempDir()"]
SHARED_PATHS = ["/tmp/", "./report"]


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    text = "\n".join(p.read_text(errors="ignore") for p in root.rglob("*_test.go"))
    low = text.lower()
    errors = []
    if "t.tempdir()" not in low:
        errors.append("missing t.TempDir isolation")
    if not re.search(r"type\s+\w*(fake|recording)\w*notifier", low):
        errors.append("missing purpose-built fake/recording notifier")
    if any(bad.lower() in low for bad in BAD_IMPORTS):
        errors.append("uses real network/global temp dependency")
    if any(path in text for path in SHARED_PATHS):
        errors.append("uses shared filesystem path")
    if "write failure" not in low and "writefailure" not in low and "permission" not in low:
        errors.append("missing write-failure case")
    if "notifier failure" not in low and "notify failure" not in low and "notifier error" not in low and "notify error" not in low and "notifyerror" not in low:
        errors.append("missing notifier-failure case")
    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
