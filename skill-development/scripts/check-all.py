#!/usr/bin/env python3
"""Run all local non-LLM gates for the testing-best-practices skill."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = [
    [sys.executable, "scripts/static-audit.py"],
    [sys.executable, "scripts/score-evals.py", "--evals", "evals/evals.json"],
    [
        "skill-benchmark",
        "validate",
        "../evals/shared-benchmark.json",
        "--strict-leakage",
        "--leakage-min-chars",
        "1",
        "--check-ablations",
    ],
    [
        "skill-benchmark",
        "audit-manifest",
        "../evals/shared-benchmark.json",
        "--fail-on-blockers",
    ],
    [sys.executable, "scripts/run-fixture-oracles.py"],
    [sys.executable, "scripts/test-gtb-output-adapter.py"],
    [sys.executable, "scripts/test-run-prompt-evals.py"],
    [sys.executable, "scripts/run-mini-repos.py"],
    [sys.executable, "scripts/test-untrusted-oracles.py"],
    [sys.executable, "scripts/test-harness-workflow.py"],
    [sys.executable, "scripts/verify-issues20-21-attestation.py"],
    [sys.executable, "scripts/eval-health-report.py"],
    [sys.executable, "scripts/audit-best-practices.py"],
    [sys.executable, "scripts/score-skill-version.py", "--skill-root", "../testing-best-practices"],
]


def main() -> int:
    for cmd in COMMANDS:
        print(f"\n$ {' '.join(cmd)}")
        proc = subprocess.run(cmd, cwd=ROOT)
        if proc.returncode != 0:
            return proc.returncode
    print("\nOK: all local gates passed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
