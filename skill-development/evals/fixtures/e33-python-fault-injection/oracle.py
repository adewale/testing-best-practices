#!/usr/bin/env python3
"""Grade executed candidate behavior, rather than source keywords."""

from __future__ import annotations

import sys
from pathlib import Path

FIXTURE = Path(__file__).resolve().parent
sys.path.insert(0, str(FIXTURE.parents[1]))
from behavioral_oracle import grade

REFERENCE = (FIXTURE / "impl/report.py").read_text()


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    return grade(
        root,
        FIXTURE,
        {"report.py": REFERENCE},
        {
            "does not retry transient failures": {
                "report.py": REFERENCE.replace("if attempt == 2:", "if True:")
            },
            "leaks raw dependency exception": {
                "report.py": REFERENCE.replace(
                    'raise ReportSaveError("could not save report") from error', "raise"
                )
            },
            "swallows exhausted failures": {
                "report.py": REFERENCE.replace(
                    'raise ReportSaveError("could not save report") from error',
                    "return key",
                )
            },
        },
    )


if __name__ == "__main__":
    raise SystemExit(main())
