#!/usr/bin/env python3
"""Validate eval suite shape and print taxonomy coverage.

Stdlib-only by design. This is not a prompt runner; it makes the eval set
machine-checkable so manual/LLM prompt scoring has stable inputs.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

REQUIRED_TOP = {"skill_name", "version", "how_to_use", "evals"}
REQUIRED_EVAL = {
    "id",
    "critical",
    "mode",
    "taxonomy",
    "prompt",
    "fixture",
    "expected_behavior",
    "red_flags",
    "rubric_focus",
    "measurement",
    "validity",
    "eval_health",
}
REQUIRED_VALIDITY = {"claim", "warrant", "backing", "rebuttals"}
REQUIRED_EVAL_HEALTH = {"difficulty", "saturation_status", "known_discriminates_versions", "last_reviewed"}
DIFFICULTIES = {"easy", "medium", "hard", "adversarial"}
SATURATION_STATUSES = {"unknown", "saturated_public", "hidden_probe", "active", "retired"}
REQUIRED_TAXONOMY = {"language_framework", "techniques", "risk_classes", "failure_modes"}
REQUIRED_MEASUREMENT = {"static_checks", "runtime_checks", "judge_checks"}
MODES = {"write", "assess", "upgrade", "detect"}
RUBRIC_DIMS = set("ABCDEFGH")
MIN_TECHNIQUES = {
    "property-based",
    "deterministic-time",
    "vcr-recorded-fixture",
    "contract",
    "golden-snapshot",
    "characterization",
    "differential",
    "mutation",
    "doc-sync",
    "test-data-builder",
    "correctness-by-construction",
}
MIN_LANG_PREFIXES = ["generic", "python", "typescript", "go", "rust", "unsupported"]
CORE_LANGUAGE_MIN_COUNTS = {
    "python": 2,
    "go": 2,
    "typescript": 2,
    "rust": 2,
}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def validate(data: dict) -> tuple[list[str], dict[str, Counter]]:
    errors: list[str] = []
    missing = REQUIRED_TOP - set(data)
    if missing:
        fail(errors, f"top-level missing fields: {sorted(missing)}")
    if data.get("skill_name") != "testing-best-practices":
        fail(errors, "skill_name must be testing-best-practices")
    evals = data.get("evals")
    if not isinstance(evals, list) or not evals:
        fail(errors, "evals must be a non-empty list")
        return errors, {}

    ids: set[str] = set()
    counters: dict[str, Counter] = defaultdict(Counter)
    for i, ev in enumerate(evals):
        if not isinstance(ev, dict):
            fail(errors, f"eval[{i}] is not an object")
            continue
        ev_id = ev.get("id", f"eval[{i}]")
        if ev_id in ids:
            fail(errors, f"duplicate eval id: {ev_id}")
        ids.add(ev_id)
        missing = REQUIRED_EVAL - set(ev)
        if missing:
            fail(errors, f"{ev_id}: missing fields {sorted(missing)}")
        if ev.get("mode") not in MODES:
            fail(errors, f"{ev_id}: invalid mode {ev.get('mode')!r}")
        if not isinstance(ev.get("critical"), bool):
            fail(errors, f"{ev_id}: critical must be boolean")
        focus = ev.get("rubric_focus", [])
        if not isinstance(focus, list) or not focus or any(dim not in RUBRIC_DIMS for dim in focus):
            fail(errors, f"{ev_id}: rubric_focus must use A-H")
        for field in ["expected_behavior", "red_flags"]:
            if not isinstance(ev.get(field), list) or not ev[field]:
                fail(errors, f"{ev_id}: {field} must be non-empty list")
        tax = ev.get("taxonomy", {})
        if not isinstance(tax, dict):
            fail(errors, f"{ev_id}: taxonomy must be object")
            tax = {}
        missing_tax = REQUIRED_TAXONOMY - set(tax)
        if missing_tax:
            fail(errors, f"{ev_id}: taxonomy missing {sorted(missing_tax)}")
        lang = tax.get("language_framework")
        if isinstance(lang, str):
            counters["language_framework"][lang] += 1
        for key in ["techniques", "risk_classes", "failure_modes"]:
            values = tax.get(key)
            if not isinstance(values, list) or not values:
                fail(errors, f"{ev_id}: taxonomy.{key} must be non-empty list")
            else:
                counters[key].update(values)
        meas = ev.get("measurement", {})
        if not isinstance(meas, dict):
            fail(errors, f"{ev_id}: measurement must be object")
            meas = {}
        missing_meas = REQUIRED_MEASUREMENT - set(meas)
        if missing_meas:
            fail(errors, f"{ev_id}: measurement missing {sorted(missing_meas)}")
        for key in REQUIRED_MEASUREMENT:
            if key in meas and not isinstance(meas[key], list):
                fail(errors, f"{ev_id}: measurement.{key} must be list")
        validity = ev.get("validity", {})
        if not isinstance(validity, dict):
            fail(errors, f"{ev_id}: validity must be object")
            validity = {}
        missing_validity = REQUIRED_VALIDITY - set(validity)
        if missing_validity:
            fail(errors, f"{ev_id}: validity missing {sorted(missing_validity)}")
        if not isinstance(validity.get("rebuttals", []), list) or not validity.get("rebuttals"):
            fail(errors, f"{ev_id}: validity.rebuttals must be non-empty list")
        health = ev.get("eval_health", {})
        if not isinstance(health, dict):
            fail(errors, f"{ev_id}: eval_health must be object")
            health = {}
        missing_health = REQUIRED_EVAL_HEALTH - set(health)
        if missing_health:
            fail(errors, f"{ev_id}: eval_health missing {sorted(missing_health)}")
        if health.get("difficulty") not in DIFFICULTIES:
            fail(errors, f"{ev_id}: invalid eval_health.difficulty {health.get('difficulty')!r}")
        if health.get("saturation_status") not in SATURATION_STATUSES:
            fail(errors, f"{ev_id}: invalid eval_health.saturation_status {health.get('saturation_status')!r}")
        if not isinstance(health.get("known_discriminates_versions", []), list):
            fail(errors, f"{ev_id}: eval_health.known_discriminates_versions must be list")
        if "hidden" in ev and not isinstance(ev["hidden"], bool):
            fail(errors, f"{ev_id}: hidden must be boolean when present")
        counters["mode"][ev.get("mode")] += 1
        counters["critical"]["critical" if ev.get("critical") else "noncritical"] += 1

    missing_modes = MODES - set(counters["mode"])
    if missing_modes:
        fail(errors, f"missing mode coverage: {sorted(missing_modes)}")
    missing_techniques = MIN_TECHNIQUES - set(counters["techniques"])
    if missing_techniques:
        fail(errors, f"missing required technique coverage: {sorted(missing_techniques)}")
    langs = set(counters["language_framework"])
    missing_langs = [prefix for prefix in MIN_LANG_PREFIXES if not any(lang.startswith(prefix) for lang in langs)]
    if missing_langs:
        fail(errors, f"missing language/framework coverage: {missing_langs}")
    for prefix, minimum in CORE_LANGUAGE_MIN_COUNTS.items():
        count = sum(n for lang, n in counters["language_framework"].items() if lang.startswith(prefix))
        if count < minimum:
            fail(errors, f"core language {prefix!r} has {count} evals; expected at least {minimum}")
    for prefix in CORE_LANGUAGE_MIN_COUNTS:
        critical_count = sum(
            1
            for ev in evals
            if ev.get("critical") and isinstance(ev.get("taxonomy"), dict)
            and str(ev["taxonomy"].get("language_framework", "")).startswith(prefix)
        )
        if critical_count < 1:
            fail(errors, f"core language {prefix!r} needs at least one critical eval")
    for ev in evals:
        if ev.get("critical"):
            meas = ev.get("measurement", {})
            if not meas.get("runtime_checks") and not meas.get("static_checks"):
                fail(errors, f"{ev.get('id')}: critical eval needs static or runtime measurement")
    return errors, counters


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evals", default="evals/evals.json")
    args = parser.parse_args()
    path = Path(args.evals)
    try:
        data = json.loads(path.read_text())
    except Exception as exc:
        print(f"ERROR: failed to read {path}: {exc}", file=sys.stderr)
        return 2
    errors, counters = validate(data)
    print(f"evals: {len(data.get('evals', []))}")
    for key in ["mode", "critical", "language_framework", "techniques", "risk_classes", "failure_modes"]:
        print(f"\n[{key}]")
        for item, count in sorted(counters.get(key, {}).items()):
            print(f"  {item}: {count}")
    if errors:
        print("\nVALIDATION FAILED", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1
    print("\nOK: eval suite shape and coverage checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
