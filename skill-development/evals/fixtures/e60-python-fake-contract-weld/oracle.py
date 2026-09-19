#!/usr/bin/env python3
"""Oracle for E60: candidate tests must weld the fake to the real store.

Three pytest runs decide:
  1. pristine impls           -> candidate tests must PASS
  2. drifted fake (get() returns None on missing keys) -> must FAIL
  3. drifted real (get() returns None on missing keys) -> must FAIL

Run 2 catches a suite that never checks the fake's contract; run 3 catches a
suite that checks the fake but never runs the same expectations against the
real implementation. Only a shared contract suite executed against BOTH
implementations passes all three — which is the lesson (Google Testing Blog:
Fake Your Way to Better Tests, 2013; Exercise Service Call Contracts, 2018).
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FIXTURE = Path(__file__).resolve().parent
REAL = (FIXTURE / "impl" / "store.py").read_text()
FAKE = (FIXTURE / "impl" / "fake_store.py").read_text()

DRIFT_FAKE = FAKE.replace(
    "        if key not in self._data:\n            raise KeyError(key)\n        return self._data[key]",
    "        return self._data.get(key)",
)
DRIFT_REAL = REAL.replace(
    "        if row is None:\n            raise KeyError(key)\n        return row[0]",
    "        return row[0] if row is not None else None",
)


def run_pytest(store_src: str, fake_src: str, candidate_files: list[Path]) -> tuple[bool, str]:
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "store.py").write_text(store_src)
        (d / "fake_store.py").write_text(fake_src)
        for f in candidate_files:
            shutil.copy(f, d / f.name)
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
            cwd=d, env=env, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180,
        )
        return proc.returncode == 0, proc.stdout[-1500:]


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    candidates = sorted(
        p for p in root.rglob("*.py")
        if p.name.startswith("test") or p.name.endswith("_test.py") or p.name == "conftest.py"
    )
    if not candidates:
        print("no test files (test*.py / conftest.py) found in candidate dir", file=sys.stderr)
        return 1
    for name, drifted, original in [("fake", DRIFT_FAKE, FAKE), ("real", DRIFT_REAL, REAL)]:
        if drifted == original:
            print(f"oracle self-error: {name} drift substitution failed", file=sys.stderr)
            return 2

    errors: list[str] = []
    ok, out = run_pytest(REAL, FAKE, candidates)
    if not ok:
        errors.append(f"candidate tests FAIL against the pristine implementations:\n{out}")
    else:
        ok, _ = run_pytest(REAL, DRIFT_FAKE, candidates)
        if ok:
            errors.append(
                "drifted FAKE survived: tests pass although FakeStore.get now returns "
                "None on missing keys (the shipped-bug scenario repeats)"
            )
        ok, _ = run_pytest(DRIFT_REAL, FAKE, candidates)
        if ok:
            errors.append(
                "drifted REAL survived: the contract expectations never run against "
                "RealStore, so the fake is only honest with itself"
            )

    for e in errors:
        print(e, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
