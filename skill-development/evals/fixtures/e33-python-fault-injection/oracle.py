#!/usr/bin/env python3
"""Exercise transient recovery and the terminal error contract independently."""

import sys
from pathlib import Path

FIXTURE = Path(__file__).resolve().parent
sys.path.insert(0, str(FIXTURE.parents[1]))
from behavioral_oracle import grade


def main() -> int:
    report = (FIXTURE / "impl/report.py").read_text()
    wrapped = 'raise ReportSaveError("could not save report") from error'
    return grade(
        FIXTURE,
        {"report.py": report},
        {
            "loses a successful retry": {
                "report.py": report.replace(
                    "            return key",
                    '            if attempt:\n                raise ReportSaveError("retry lost")\n            return key',
                )
            },
            "abandons third attempt": {
                "report.py": report.replace("if attempt == 2:", "if attempt == 1:")
            },
            "leaks raw dependency error": {
                "report.py": report.replace(wrapped, "raise")
            },
            "swallows exhausted failure": {
                "report.py": report.replace(wrapped, "return key")
            },
        },
    )


if __name__ == "__main__":
    raise SystemExit(main())
