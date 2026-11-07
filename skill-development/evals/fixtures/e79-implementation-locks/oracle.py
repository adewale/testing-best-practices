#!/usr/bin/env python3
"""Require semantic preservation and integrity, including an allowed refactor."""

from __future__ import annotations

import sys
from pathlib import Path

FIXTURE = Path(__file__).resolve().parent
sys.path.insert(0, str(FIXTURE.parents[1]))
from behavioral_oracle import grade

REFERENCE = (FIXTURE / "impl/catalog.py").read_text()


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    return grade(
        root,
        FIXTURE,
        {"catalog.py": REFERENCE},
        {
            "drops labels": {
                "catalog.py": REFERENCE.replace(
                    '{"items": items}',
                    '{"items": [{"id": item["id"]} for item in items]}',
                )
            },
            "reorders items": {
                "catalog.py": REFERENCE.replace(
                    '{"items": items}', '{"items": list(reversed(items))}'
                )
            },
            "accepts corrupted bytes": {
                "catalog.py": REFERENCE.replace(
                    "if hashlib.sha256(payload).hexdigest() != expected_sha256:",
                    "if False:",
                )
            },
        },
        equivalents={
            "JSON whitespace and object key order": {
                "catalog.py": REFERENCE.replace(
                    'separators=(",", ":")', "indent=2, sort_keys=True"
                ),
            },
        },
    )


if __name__ == "__main__":
    raise SystemExit(main())
