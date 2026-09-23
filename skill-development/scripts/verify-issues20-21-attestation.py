#!/usr/bin/env python3
"""Verify reproducible hashes in the issues #20/#21 harness attestation."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ATTESTATION = ROOT / "skill-development/evals/attestations/issues-20-21-multimodel.json"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_sha256(base: Path) -> str:
    digest = hashlib.sha256()
    files = sorted(path for path in base.rglob("*") if path.is_file() and "__pycache__" not in path.parts)
    for path in files:
        digest.update(str(path.relative_to(base)).encode() + b"\0" + path.read_bytes() + b"\0")
    return digest.hexdigest()


def run_sha256(base: Path, *, historical: bool) -> tuple[str, int]:
    digest = hashlib.sha256()
    allowed = {"output.md", "metadata.json", "trace.jsonl"}
    files = sorted(
        path for path in base.rglob("*")
        if path.is_file() and (not historical or path.name in allowed)
    )
    for path in files:
        digest.update(
            str(path.relative_to(base)).encode()
            + b"\0"
            + hashlib.sha256(path.read_bytes()).digest()
        )
    return digest.hexdigest(), len(files)


def check(label: str, actual: object, expected: object, errors: list[str]) -> None:
    if actual != expected:
        errors.append(f"{label}: expected {expected!r}, got {actual!r}")
    else:
        print(f"OK: {label}")


def main() -> int:
    attestation = json.loads(ATTESTATION.read_text())
    errors: list[str] = []
    print("INFO: historical manifest hash is authentication-only; its exact preimage was not retained.")
    print(
        "INFO: historical oracle_tree_sha256_at_attestation is authentication-only; "
        "the suite was renumbered and combined with upstream fixtures after generation."
    )
    print(
        "INFO: historical generation.skill_tree_sha256 is authentication-only; "
        "upstream skill changes landed before this PR was rebased."
    )
    check(
        "pinned old skill tree",
        tree_sha256(ROOT / "skill-development/github-skill-origin-main/testing-best-practices"),
        attestation["old_skill"]["tree_sha256"],
        errors,
    )

    current = attestation["current_harness_compatibility"]
    check("current manifest", file_sha256(ROOT / "evals/shared-benchmark.json"), current["manifest_sha256"], errors)
    for relative, expected in current["current_reproduction_script_sha256"].items():
        check(f"current script {relative}", file_sha256(ROOT / relative), expected, errors)

    historical_runs = ROOT / "skill-development/eval-runs/skill-harness-issues20-21-repeat3"
    if historical_runs.is_dir():
        for model, expected in attestation["generation"]["run_tree_digests"].items():
            actual_hash, count = run_sha256(historical_runs / model, historical=True)
            check(f"historical run tree {model} hash", actual_hash, expected["sha256"], errors)
            check(f"historical run tree {model} file count", count, expected["files"], errors)
    else:
        print("SKIP: ignored historical run trees are absent")

    smoke = ROOT / "skill-development/eval-runs/skill-harness-v060-smoke/gpt-5.6-sol"
    expected_smoke = current["pre_rebase_native_codex_smoke"]["run_tree_digest"]
    if smoke.is_dir():
        actual_hash, count = run_sha256(smoke, historical=False)
        check("v0.6 smoke run tree hash", actual_hash, expected_smoke["sha256"], errors)
        check("v0.6 smoke run tree file count", count, expected_smoke["files"], errors)
    else:
        print("SKIP: ignored v0.6 smoke run tree is absent")

    print(
        "INFO: prepared_tasks_sha256 is authentication-only; its ignored exact "
        "preimage was not retained and cannot be reconstructed from candidate artifacts."
    )
    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
