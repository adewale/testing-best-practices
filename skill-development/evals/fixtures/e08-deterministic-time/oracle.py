#!/usr/bin/env python3
"""Run candidate tests against the scheduler and three wrong delivery behaviors."""

import sys
from pathlib import Path

FIXTURE = Path(__file__).resolve().parent
sys.path.insert(0, str(FIXTURE.parents[1]))
from behavioral_oracle import grade


def main() -> int:
    module = "app/scheduler.py"
    scheduler = (FIXTURE / "impl" / module).read_text()
    return grade(
        FIXTURE,
        {
            module: scheduler,
            "app/__init__.py": "",
            "_tbp_fixture.py": (FIXTURE / "impl/no_wall_clock_sleep.py").read_text(),
        },
        {
            "runs before deadline": {
                module: scheduler.replace("if due <= self.clock.now", "if True")
            },
            "never runs scheduled job": {
                module: scheduler.replace("callback()", "pass")
            },
            "repeats completed job": {
                module: scheduler.replace("if due > self.clock.now", "if True")
            },
        },
    )


if __name__ == "__main__":
    raise SystemExit(main())
