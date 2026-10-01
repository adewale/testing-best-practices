#!/usr/bin/env python3
"""Oracle for E78: kill the real survivor, classify the equivalent ones.

Runtime oracle. The candidate tests must pass against the correct module and fail
against the boundary mutant (a real gap). They must pass against the tie-break and
cache mutants: both are equivalent through the public interface, so a test that
kills them is exercising a private helper or poisoning the cache.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(tests: list[Path], impl: Path) -> int:
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        shutil.copy(impl, t / "keyphrase.py")
        for f in tests:
            shutil.copy(f, t / f.name)
        return subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
                              cwd=t, capture_output=True, text=True).returncode


def main() -> int:
    tests = sorted(Path(sys.argv[1]).rglob("test_*.py"))
    if not tests:
        print("no test file", file=sys.stderr)
        return 1
    errors = []
    if run(tests, HERE / "src" / "keyphrase.py") != 0:
        errors.append("tests fail against the correct implementation")
    else:
        if run(tests, HERE / "mutants" / "boundary" / "keyphrase.py") == 0:
            errors.append("the real survivor (MIN_SCORE boundary) is still alive")
        for name, why in (("tiebreak", "tests a private tie-break no public input can reach"),
                          ("cache", "poisons or inspects the cache to kill a speed-only mutant")):
            if run(tests, HERE / "mutants" / name / "keyphrase.py") != 0:
                errors.append(f"kills an equivalent mutant: {why}")
    for e in errors:
        print(e, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
