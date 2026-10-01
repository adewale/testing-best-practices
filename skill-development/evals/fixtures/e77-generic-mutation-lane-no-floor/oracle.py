#!/usr/bin/env python3
"""Oracle for E77: don't give a calendar mutation lane "teeth" with a floor.

The lane re-scores unchanged code weekly with identical results. Passing shape:
removes or replaces the calendar schedule (change-based trigger, on demand).
Failing shape: adds a numeric `break` floor and keeps the weekly schedule, or never
addresses the schedule at all.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

NEG = re.compile(r"(\bnot\b|n't|\bnever\b|\bno\b|\bwithout\b)[^.\n]{0,15}$")


def unnegated(pattern: str, text: str) -> bool:
    for m in re.finditer(pattern, text):
        if not NEG.search(text[max(0, m.start() - 30):m.start()]):
            return True
    return False


def main() -> int:
    low = "\n".join(p.read_text(errors="ignore") for p in Path(sys.argv[1]).rglob("*.md")).lower()
    low = re.sub(r"\s+", " ", low)
    changes_trigger = unnegated(
        r"(remove|delete|drop|stop|replace|get rid of)[^.]{0,40}(schedule|cron|weekly|monday)", low
    ) or re.search(r"(workflow_dispatch|on demand|on-demand|--incremental|--diff|paths:|paths filter"
                   r"|pull requests? that (touch|change)|changed (code|files))", low)
    floor = unnegated(r"(set|add|use|configure|change)[^.\n]{0,25}\bbreak\b[^.\n]{0,8}\b[1-9]\d\b", low) or \
        re.search(r"\"?break\"?\s*:\s*[1-9]\d\b", low)
    keeps_schedule = unnegated(r"keep[^.\n]{0,20}(schedule|cron|weekly|monday)", low)
    errors = []
    if not changes_trigger:
        errors.append("leaves the calendar schedule re-scoring unchanged code")
    if floor and keeps_schedule:
        errors.append("adds a numeric floor to a weekly lane over unchanged code")
    for e in errors:
        print(e, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
