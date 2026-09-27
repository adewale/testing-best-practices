#!/usr/bin/env python3
"""Oracle for E76: visual tests must run in CI on CI-rendered baselines, and
required lanes must not retry.

Structural checks over the candidate files:
- no CI-conditional (or positive) Playwright retries;
- the spec uses toHaveScreenshot and is not skipped/fixme'd on CI;
- some workflow or instruction generates baselines on the CI image
  (`--update-snapshots` together with workflow_dispatch/container/CI image).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    root = Path(sys.argv[1])
    files = {p: p.read_text(errors="ignore") for p in root.rglob("*") if p.is_file()}
    text = "\n".join(files.values())
    ts = "\n".join(t for p, t in files.items() if p.suffix == ".ts")
    errors = []
    if re.search(r"retries:\s*process\.env\.CI\s*\?\s*[1-9]", ts) or re.search(r"retries:\s*[1-9]", ts):
        errors.append("required lane still retries failures")
    if "toHaveScreenshot" not in ts:
        errors.append("no visual assertion (toHaveScreenshot)")
    if re.search(r"test(\.describe)?\.(skip|fixme)\([^)]*(process\.env\.CI|isCI)", ts):
        errors.append("visual test is skipped on CI")
    if not (re.search(r"--update-snapshots", text) and
            re.search(r"workflow_dispatch|mcr\.microsoft\.com/playwright|container|ci image|same image", text, re.IGNORECASE)):
        errors.append("no way to render baselines on the CI image")
    for e in errors:
        print(e, file=sys.stderr)
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
