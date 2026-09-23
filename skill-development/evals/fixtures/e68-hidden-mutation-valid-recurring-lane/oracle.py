#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    text = "\n".join(path.read_text(errors="ignore") for path in root.rglob("*.md"))
    text = text.lower().replace("*", "").replace("`", "").split("acceptance-report", 1)[0]
    errors: list[str] = []

    approval = re.search(
        r"(?:yes.{0,25}|approve|recommend|proceed with|safe to|should|can)\s*(?:approve|schedule|enable|run|proceed)?[^.\n]{0,55}(?:lane|protected[- ]branch|schedul)|(?:schedule|enable|run|proceed with)[^.\n]{0,45}(?:focused|changed[- ]code|authorization)\s+lane",
        text,
    )
    if not approval:
        errors.append("does not clearly approve running the justified lane")

    refusal = re.search(
        r"(?:cannot|can.?t|do not|don.?t|should not|must not|will not|won.?t)\s+(?:approve|schedule|run|enable)\b|(?:postpone|defer|withhold|decline)\b.{0,35}(?:lane|schedule|run)|(?:stay|remain)\s+manual|approve.{0,25}in principle.{0,80}(?:but|however).{0,50}(?:not|never|manual)|(?:protected[- ]branch).{0,35}should not run",
        text,
        re.DOTALL,
    )
    if refusal:
        errors.append("refuses, postpones, or only nominally approves a lane that satisfies the operating contract")

    checks = [
        (
            r"seeded|sabotage|repaired fault|regression|oracle bite|killed|named.{0,30}fault|authorization[- ]bypass",
            "ignores demonstrated fault-class/oracle bite",
        ),
        (r"baseline|retained|six", "ignores completed baseline history"),
        (r"45|65|minute|timeout|capacity|budget", "ignores measured capacity"),
        (r"owner|security team|annotation|page|notify", "ignores ownership/action path"),
        (r"changed[- ]code|actionable survivor|focused|authorization", "ignores focused actionable scope"),
        (r"quarter|90 days|expiry|auto[- ]disable|removal", "ignores expiry/removal policy"),
    ]
    for pattern, message in checks:
        if not re.search(pattern, text):
            errors.append(message)

    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
