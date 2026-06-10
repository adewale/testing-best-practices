#!/usr/bin/env python3
"""Oracle for E33: error-handling paths must be exercised by injected failure.

A passing suite injects a downstream/dependency failure (a fake/stub that
raises, or a mock ``side_effect`` exception) AND asserts the system handles it
(retries, wraps the error, releases resources). Rejecting invalid *arguments*
with ``pytest.raises`` does not count: that is input validation, not an
error-handling path triggered by a failing dependency.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Exceptions that model a failing dependency/environment rather than bad input.
FAILURE_EXCEPTIONS = (
    "ConnectionError",
    "TimeoutError",
    "OSError",
    "IOError",
    "BrokenPipeError",
    "ConnectionResetError",
)


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    text = "\n".join(p.read_text(errors="ignore") for p in root.rglob("*.py"))
    low = text.lower()
    errors: list[str] = []

    # 1. A downstream failure must be injected: either a mock side_effect set to
    #    a failure exception, or a fake/stub whose method raises one.
    side_effect_failure = bool(
        re.search(
            r"side_effect\s*=\s*[^\n]*(" + "|".join(FAILURE_EXCEPTIONS) + ")",
            text,
        )
    )
    raises_in_fake = bool(
        re.search(r"\braise\s+(" + "|".join(FAILURE_EXCEPTIONS) + r")\b", text)
    )
    if not (side_effect_failure or raises_in_fake):
        errors.append(
            "no injected downstream failure (failing fake or side_effect "
            "exception); only happy-path / argument validation is tested"
        )

    # 2. The error-handling outcome must be asserted: a retry/recovery check or
    #    a wrapped structured failure (ReportSaveError), not the raw exception.
    asserts_handling = bool(
        re.search(r"pytest\.raises\(\s*reportsaveerror", low)
        or "call_count" in low
        or re.search(r"\.call_count\b", low)
        or "retr" in low  # retry / retries / retried
        or re.search(r"assert[^\n]*recover", low)
    )
    if not asserts_handling:
        errors.append(
            "downstream failure injected but error-handling behavior not "
            "asserted (no retry/recovery assertion and no wrapped-error check)"
        )

    # 3. Basic sanity: real assertions exist.
    if "assert" not in low:
        errors.append("no assertions found")

    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
