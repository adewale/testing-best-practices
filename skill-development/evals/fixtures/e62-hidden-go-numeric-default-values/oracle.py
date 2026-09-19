#!/usr/bin/env python3
"""Oracle for E62 (hidden hardened variant of E56): the package doc examples
deliberately tempt with zero values (account 0, amount 0). Candidate Go tests
must pass the real implementation and kill two seeded mutants:

  - ignore_id:     Add credits account 0 regardless of accountID. Survives
                   suites that only ever use account 0.
  - ignore_amount: Add credits nothing. Survives suites that only add zero
                   amounts (or never compare balances to a non-zero value).

Distinct, non-default IDs and amounts kill both.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FIXTURE = Path(__file__).resolve().parent
REAL = (FIXTURE / "impl" / "ledger.go").read_text()
MUTANTS = {
    "ignore_id": REAL.replace(
        "func (l *Ledger) Add(accountID, amount int) { l.m[accountID] += amount }",
        "func (l *Ledger) Add(accountID, amount int) { l.m[0] += amount }",
    ),
    "ignore_amount": REAL.replace(
        "func (l *Ledger) Add(accountID, amount int) { l.m[accountID] += amount }",
        "func (l *Ledger) Add(accountID, amount int) { l.m[accountID] += 0 }",
    ),
}
GO_MOD = "module ledgertest\n\ngo 1.21\n"


def run_go_test(impl_src: str, test_files: list[Path]) -> tuple[bool, str]:
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "go.mod").write_text(GO_MOD)
        (d / "ledger.go").write_text(impl_src)
        for tf in test_files:
            shutil.copy(tf, d / tf.name)
        env = os.environ.copy()
        env.update({"GOFLAGS": "-mod=mod", "GOPROXY": "off", "GOCACHE": str(d / ".gocache")})
        proc = subprocess.run(
            ["go", "test", "./..."],
            cwd=d, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            env=env, timeout=180,
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
                    f"mutant '{name}' SURVIVED: tests pass with a broken Add "
                    "(zero-value account IDs/amounts copied from the doc example)"
                )

    for e in errors:
        print(e, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
