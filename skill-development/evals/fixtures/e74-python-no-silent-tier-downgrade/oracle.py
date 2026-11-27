#!/usr/bin/env python3
"""Check partial matching and rank failures observed during a real SQLite search."""

import sys
from pathlib import Path

FIXTURE = Path(__file__).resolve().parent
sys.path.insert(0, str(FIXTURE.parents[1]))
from behavioral_oracle import grade


def main() -> int:
    reference = (FIXTURE / "src/search.py").read_text()
    order = "SQLite ranks lowest score first"
    return grade(
        FIXTURE,
        {
            "search.py": reference,
            "_tbp_fixture.py": (FIXTURE / "sqlite_observer.py").read_text(),
        },
        {
            "wildcards dropped": {"search.py": (FIXTURE / "mutant/search.py").read_text()},
            order: {
                "search.py": (FIXTURE / "mutant-order/search.py").read_text(),
                "_tbp_search_reference.py": reference,
            },
        },
        required_observations={order: "ran the owned search on SQLite"},
    )


if __name__ == "__main__":
    raise SystemExit(main())
