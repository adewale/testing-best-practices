#!/usr/bin/env python3
from __future__ import annotations
import re, sys
from pathlib import Path


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    text = "\n".join(p.read_text(errors="ignore") for p in root.rglob("*.md")).lower().replace("*", "").replace("`", "")
    text = text.split("acceptance-report", 1)[0]
    errors = []
    if not re.search(r"\b(yes|approve|proceed|should schedule|schedule it|recommend scheduling)\b", text):
        errors.append("does not clearly approve the justified lane")
    if re.search(r"do not approve|don.?t approve|cannot approve|can.?t approve|\bdecline\b|withhold approval|(?<!do not )(?<!don.t )\breject (?:it|this|the)|not yet|should not schedule|must not schedule|do not schedule|don.?t schedule|stay manual|remain manual", text):
        errors.append("refuses or defers a lane that satisfies the operating contract")
    for pattern, message in [
        (r"seeded|sabotage|repaired fault|regression|oracle bite|killed|named.{0,30}fault|authorization[- ]bypass", "ignores demonstrated fault-class/oracle bite"),
        (r"baseline|retained|six", "ignores completed baseline history"),
        (r"45|65|minute|timeout|capacity|budget", "ignores measured capacity"),
        (r"owner|security team|annotation|page|notify", "ignores ownership/action path"),
        (r"changed[- ]code|actionable survivor|focused|authorization", "ignores focused actionable scope"),
        (r"quarter|90 days|expiry|auto[- ]disable|removal", "ignores expiry/removal policy"),
    ]:
        if not re.search(pattern, text): errors.append(message)
    for error in errors: print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
