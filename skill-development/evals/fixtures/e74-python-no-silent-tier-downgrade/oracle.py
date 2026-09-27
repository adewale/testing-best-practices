#!/usr/bin/env python3
"""Oracle for E74: a cleanup must not silently downgrade a real-engine test.

Runtime oracle: the cleaned-up tests must pass against the correct implementation
and fail against a mutant that drops the LIKE wildcards. Only a test that runs the
query on real SQLite catches it; SQL-substring and mocked-cursor rewrites pass.
"""
from __future__ import annotations
import shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

def run(tests: list[Path], impl: Path) -> int:
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        shutil.copy(impl, t / "search.py")
        for f in tests:
            shutil.copy(f, t / f.name)
        return subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
                              cwd=t, capture_output=True, text=True).returncode

def main() -> int:
    tests = sorted(Path(sys.argv[1]).rglob("test_*.py"))
    if not tests:
        print("no test file", file=sys.stderr); return 1
    if run(tests, HERE / "src" / "search.py") != 0:
        print("cleaned-up tests fail against the correct implementation", file=sys.stderr); return 1
    if run(tests, HERE / "mutant" / "search.py") == 0:
        print("cleanup removed the real-SQLite behavior test: a wildcard bug now passes", file=sys.stderr); return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
