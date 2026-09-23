#!/usr/bin/env python3
"""Prove shared/local E67 grading never executes model-generated Python."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHARED = ROOT / "evals/oracles/development_fixture_oracle.py"
FIXTURE = ROOT / "skill-development/evals/fixtures/e67-combinatorial-registry-sabotage/oracle.py"
GOOD = ROOT / "skill-development/evals/fixtures/e67-combinatorial-registry-sabotage/samples/good"


def run(command: list[str]) -> None:
    proc = subprocess.run(command, text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(f"command failed: {command}\nstdout={proc.stdout}\nstderr={proc.stderr}")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="tbp-untrusted-oracle-") as directory:
        root = Path(directory)
        marker = root / "MODEL_CODE_EXECUTED"
        portfolio = GOOD.joinpath("portfolio.py").read_text()
        future, rest = portfolio.split("\n", 1)
        poison = (
            f"{future}\nfrom pathlib import Path\n"
            f"Path({str(marker)!r}).write_text('unsafe')\n{rest}"
        )
        tests = GOOD.joinpath("test_portfolio.py").read_text()

        candidate = root / "candidate"
        candidate.mkdir()
        candidate.joinpath("portfolio.py").write_text(poison)
        candidate.joinpath("test_portfolio.py").write_text(tests)
        run([sys.executable, str(FIXTURE), str(candidate)])
        assert not marker.exists(), "local candidate grading executed model code"

        shared = root / "shared"
        shared.mkdir()
        shared.joinpath("output.md").write_text(
            f"portfolio.py\n```python\n{poison}\n```\n"
            f"test_portfolio.py\n```python\n{tests}\n```\n"
        )
        run([
            sys.executable,
            str(SHARED),
            "e67-combinatorial-registry-sabotage",
            str(shared),
        ])
        assert not marker.exists(), "shared harness grading executed model code"

    print("OK: E67 shared/local candidate grading is static-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
