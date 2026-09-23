#!/usr/bin/env python3
"""Prepare a focused subset of Skill Eval Harness v0.6 tasks.

The native runner owns per-variant workspace isolation. This wrapper supplies
v0.6's missing stable-case selector and, when requested, removes irrelevant
all-to-all ablation rows using structured expected-regression case IDs.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "evals" / "shared-benchmark.json"
DEFAULT_CASES = (
    "pos-mutation-recurring-lane-contract,"
    "pos-mutation-survivor-triage-cuefree,"
    "pos-combinatorial-cost-aware-portfolio,"
    "pos-combinatorial-registry-sabotage,"
    "adv-mutation-valid-recurring-lane,"
    "adv-combinatorial-known-high-order-regression"
)
# Convenience aliases only. Stable manifest case IDs are the public interface.
CASE_ALIASES = {
    "E64": "pos-mutation-recurring-lane-contract",
    "E65": "pos-mutation-survivor-triage-cuefree",
    "E66": "pos-combinatorial-cost-aware-portfolio",
    "E67": "pos-combinatorial-registry-sabotage",
    "E68": "adv-mutation-valid-recurring-lane",
    "E69": "adv-combinatorial-known-high-order-regression",
}


def ablation_cases(manifest: dict, variant: str) -> set[str]:
    ablation_id = variant.removeprefix("ablation:")
    ablation = next((item for item in manifest.get("ablations", []) if item.get("id") == ablation_id), {})
    return {
        case_id
        for regression in ablation.get("expected_regressions", [])
        if isinstance(regression, dict)
        for case_id in regression.get("cases", [])
        if isinstance(case_id, str)
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--runs-per-variant", type=int, default=1)
    parser.add_argument("--cases", default=DEFAULT_CASES)
    parser.add_argument("--variants", default="with_skill,without_skill")
    parser.add_argument("--split", default="tune")
    parser.add_argument("--include-ablations", action="store_true")
    parser.add_argument("--ablation-dir", default="/tmp/tbp-harness-ablations")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text())
    requested_cases = {item.strip() for item in args.cases.split(",") if item.strip()}
    wanted_cases = {CASE_ALIASES.get(item, item) for item in requested_cases}
    known_cases = {case.get("id") for case in manifest.get("cases", []) if case.get("split") == args.split}
    unknown_cases = wanted_cases - known_cases
    if unknown_cases:
        parser.error(f"unknown {args.split} case IDs: {sorted(unknown_cases)}")

    wanted_variants = {item.strip() for item in args.variants.split(",") if item.strip()}
    valid_named = {"with_skill", "without_skill", "old_skill", "ablations"}
    invalid = {
        item for item in wanted_variants if item not in valid_named and not item.startswith("ablation:")
    }
    if invalid:
        parser.error(f"unsupported variants: {sorted(invalid)}")
    wants_ablations = "ablations" in wanted_variants or any(
        item.startswith("ablation:") for item in wanted_variants
    )
    if wants_ablations and not args.include_ablations:
        parser.error("ablation variants require --include-ablations")
    if args.include_ablations and not wants_ablations:
        parser.error("--include-ablations requires variants=ablations or a named ablation variant")

    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as handle:
        prepared = Path(handle.name)
    try:
        command = [
            "skill-benchmark",
            "prepare",
            str(MANIFEST),
            "--split",
            args.split,
            "--runs-per-variant",
            str(args.runs_per_variant),
            "--out",
            str(prepared),
        ]
        if "old_skill" in wanted_variants:
            command.append("--include-old-skill")
        if args.include_ablations:
            command.extend(["--include-ablations", "--ablation-dir", args.ablation_dir])
        subprocess.run(command, cwd=ROOT, check=True)

        rows = []
        for line in prepared.read_text().splitlines():
            task = json.loads(line)
            variant = task["variant"]
            if task["case_id"] not in wanted_cases:
                continue
            if variant.startswith("ablation:"):
                if not ({"ablations", variant} & wanted_variants):
                    continue
                if task["case_id"] not in ablation_cases(manifest, variant):
                    continue
            elif variant not in wanted_variants:
                continue
            rows.append(task)
    finally:
        prepared.unlink(missing_ok=True)

    if not rows:
        parser.error("selection produced no tasks")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    print(f"prepared {len(rows)} focused tasks in {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
