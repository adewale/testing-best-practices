#!/usr/bin/env python3
"""Oracle for E71: loop-only assertions over possibly-empty output are vacuous.

Runtime oracle: the candidate test file must pass against the correct
implementation and fail against a mutant whose threshold typo makes suggest()
return []. Loop-only tests (and `len(result) >= 0`) pass on the mutant.
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
        shutil.copy(impl, t / "geists.py")
        for f in tests:
            shutil.copy(f, t / f.name)
        proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
                              cwd=t, capture_output=True, text=True)
        return proc.returncode

def main() -> int:
    tests = sorted(Path(sys.argv[1]).rglob("test_*.py"))
    if not tests:
        print("no test file", file=sys.stderr); return 1
    if run(tests, HERE / "src" / "geists.py") != 0:
        print("tests do not pass against the correct implementation", file=sys.stderr); return 1
    if run(tests, HERE / "mutant" / "geists.py") == 0:
        print("tests still pass when suggest() returns []: assertions are vacuous", file=sys.stderr); return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
