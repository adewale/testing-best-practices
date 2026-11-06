#!/usr/bin/env python3
"""Grade executed candidate behavior, rather than source keywords."""

from __future__ import annotations

import sys
from pathlib import Path

FIXTURE = Path(__file__).resolve().parent
sys.path.insert(0, str(FIXTURE.parents[1]))
from behavioral_oracle import grade

REFERENCE = (FIXTURE / "impl/app/scheduler.py").read_text()


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    module = "app/scheduler.py"
    return grade(
        root,
        FIXTURE,
        {"app/__init__.py": "", module: REFERENCE},
        {
            "runs before deadline": {
                module: REFERENCE.replace(
                    "due <= self.clock.now", "due <= self.clock.now + 1"
                )
            },
            "never runs scheduled job": {
                module: REFERENCE.replace("callback()", "pass")
            },
            "repeats completed job": {
                module: REFERENCE.replace(
                    "if due > self.clock.now",
                    "if True",
                )
            },
        },
    )


if __name__ == "__main__":
    raise SystemExit(main())
