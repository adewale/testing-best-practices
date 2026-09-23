#!/usr/bin/env python3
"""Deterministic smoke tests for focused v0.6 task preparation."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PREPARE = ROOT / "skill-development/scripts/prepare-issue20-21-harness.py"


def prepare(*args: str) -> list[dict]:
    with tempfile.TemporaryDirectory(prefix="tbp-harness-prepare-") as directory:
        output = Path(directory) / "tasks.jsonl"
        command = [sys.executable, str(PREPARE), "--out", str(output), *args]
        subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True)
        return [json.loads(line) for line in output.read_text().splitlines()]


def main() -> int:
    paired = prepare(
        "--cases",
        "E64,E65",
        "--variants",
        "with_skill,without_skill",
    )
    assert len(paired) == 4
    assert Counter(row["variant"] for row in paired) == {"with_skill": 2, "without_skill": 2}
    assert {row["case_id"] for row in paired} == {
        "pos-mutation-recurring-lane-contract",
        "pos-mutation-survivor-triage-cuefree",
    }

    with tempfile.TemporaryDirectory(prefix="tbp-harness-ablations-") as directory:
        ablations = prepare(
            "--cases",
            "pos-api-contract-vcr,pos-cli-doc-sync,pos-parser-property",
            "--variants",
            "with_skill,ablations",
            "--include-ablations",
            "--ablation-dir",
            directory,
        )
    assert len(ablations) == 6
    assert Counter(row["variant"] for row in ablations) == {
        "with_skill": 3,
        "ablation:no-reference-matrix": 3,
    }
    assert all(
        row.get("ablation", {}).get("mode") == "materialized"
        for row in ablations
        if row["variant"].startswith("ablation:")
    )

    print("OK: focused harness preparation filters cases and ablation fanout")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
