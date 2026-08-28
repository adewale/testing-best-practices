#!/usr/bin/env python3
"""Oracle for E56: candidate Go tests must pass the real implementation and
kill two seeded mutants.

The mutants encode the "choose test values deliberately" lesson:
  - drop_value: Put stores "" instead of value. Survives tests that only use
    the string zero value (or only assert presence).
  - swap_args:  Put stores key under value. Survives tests whose key and value
    are the same string.

A test file written with distinct, non-default values per parameter kills
both. This is Voas's Execute-Infect-Propagate in runnable form: default and
duplicated values stop the infection from propagating to any assertion.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FIXTURE = Path(__file__).resolve().parent

REAL = (FIXTURE / "impl" / "kvstore.go").read_text()
MUTANTS = {
    "drop_value": REAL.replace(
        "func (s *Store) Put(key, value string) { s.m[key] = value }",
        'func (s *Store) Put(key, value string) { s.m[key] = "" }',
    ),
    "swap_args": REAL.replace(
        "func (s *Store) Put(key, value string) { s.m[key] = value }",
        "func (s *Store) Put(key, value string) { s.m[value] = key }",
    ),
}
GO_MOD = "module kvstoretest\n\ngo 1.21\n"


def run_go_test(impl_src: str, test_files: list[Path]) -> tuple[bool, str]:
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "go.mod").write_text(GO_MOD)
        (d / "kvstore.go").write_text(impl_src)
        for tf in test_files:
            shutil.copy(tf, d / tf.name)
        env = os.environ.copy()
        env.update({"GOFLAGS": "-mod=mod", "GOPROXY": "off", "GOCACHE": str(d / ".gocache")})
        proc = subprocess.run(
            ["go", "test", "./..."],
            cwd=d,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            timeout=180,
        )
        return proc.returncode == 0, proc.stdout[-2000:]


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    test_files = sorted(p for p in root.rglob("*_test.go"))
    if not test_files:
        print("no *_test.go candidate files found", file=sys.stderr)
        return 1
    for mutant in MUTANTS.values():
        if mutant == REAL:
            print("oracle self-error: mutant substitution failed", file=sys.stderr)
            return 2

    errors: list[str] = []
    ok, out = run_go_test(REAL, test_files)
    if not ok:
        errors.append(f"candidate tests FAIL against the correct implementation:\n{out}")
    else:
        for name, src in MUTANTS.items():
            ok, out = run_go_test(src, test_files)
            if ok:
                errors.append(
                    f"mutant '{name}' SURVIVED: tests pass with a broken Put "
                    "(test values are defaults or key==value)"
                )

    for e in errors:
        print(e, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
