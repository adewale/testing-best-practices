"""Bounded data-only decisions for tune cases; never execute candidate code.

A pass proves the requested decision fields, not prose quality, a working test
suite, production behavior or causal skill uplift. Keep the qualitative judge.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def boolean(plan: dict, key: str, expected: bool) -> None:
    require(type(plan.get(key)) is bool and plan[key] is expected, f"incorrect {key} decision")


def unique_object(pairs: list[tuple]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def check(fixture: str, text: str) -> None:
    require(len(text.encode("utf-8")) <= 128 * 1024, "output exceeds 128 KiB")
    fences = re.findall(r"```json\s*\n(.*?)```", text, re.IGNORECASE | re.DOTALL)
    require(len(fences) == 1, "expected exactly one JSON decision fence")
    plan = json.loads(fences[0], object_pairs_hook=unique_object)
    require(isinstance(plan, dict), "expected a decision object")

    if fixture.startswith("e64-"):
        require(set(plan) == {"schedule_now", "score_floor", "scope", "fits_single_runner", "missing_evidence"}, "incorrect decision fields")
        boolean(plan, "schedule_now", False)
        boolean(plan, "fits_single_runner", False)
        require(plan["score_floor"] is None, "copied score floor is not calibrated")
        require(plan["scope"] in {"changed_code", "critical_module"}, "scope remains repository-wide")
        require(isinstance(plan["missing_evidence"], list) and set(plan["missing_evidence"]) == {"completed_baseline", "fault_class_bite", "owner"}, "missing recurrence evidence is incorrect")
    elif fixture.startswith("e65-"):
        require(set(plan) == {"restore_70_percent", "rows"}, "incorrect decision fields")
        boolean(plan, "restore_70_percent", False)
        expected = {
            "A": "actionable_survivor", "B": "equivalent_survivor",
            "C": "timeout", "D": "compile_failure", "E": "no_coverage",
            "F": "infrastructure_failure", "G": "unobserved",
        }
        require(isinstance(plan["rows"], list) and len(plan["rows"]) == len(expected), "missing or duplicate report rows")
        observed = {}
        for row in plan["rows"]:
            require(isinstance(row, dict) and set(row) == {"id", "classification"}, "incorrect report row")
            require(isinstance(row["id"], str) and row["id"] not in observed, "duplicate or invalid report ID")
            observed[row["id"]] = row["classification"]
        require(observed == expected, "report statuses were conflated or survivors misclassified")
    elif fixture.startswith("e66-"):
        require(set(plan) == {"registry_source", "cheap_slices", "base_matrix", "elevated_group", "retain_fixed_regression", "delete_before_comparison", "costs"}, "incorrect decision fields")
        require(plan["registry_source"] == "production_registry", "registry enrollment is copied or voluntary")
        require(plan["cheap_slices"] == "exhaustive" and plan["base_matrix"] == "constrained_pairwise", "incorrect slice strategy")
        group = plan["elevated_group"]
        require(isinstance(group, list) and len(group) >= 3 and len(set(group)) == len(group), "missing named interaction group")
        require(set(group) <= {"family", "look", "palette", "format", "boundary", "runtime", "font"}, "unknown interaction factor")
        boolean(plan, "retain_fixed_regression", True)
        boolean(plan, "delete_before_comparison", False)
        costs = plan["costs"]
        require(isinstance(costs, list) and len(set(costs)) >= 3 and set(costs) <= {"runtime", "setup", "flake", "maintenance", "triage"}, "insufficient distinct cost classes")
    elif fixture.startswith("e68-"):
        require(set(plan) == {"approve", "scope", "aggregate_score_floor", "timeout_seconds", "owner", "expiry_days"}, "incorrect decision fields")
        boolean(plan, "approve", True)
        require(plan["scope"] == "changed_authorization_predicate" and plan["aggregate_score_floor"] is None, "scope or score policy changed")
        require(type(plan["timeout_seconds"]) is int and plan["timeout_seconds"] == 300, "timeout changed")
        require(plan["owner"] == "security_team" and type(plan["expiry_days"]) is int and plan["expiry_days"] == 90, "ownership or expiry changed")
    elif fixture.startswith("e69-"):
        require(set(plan) == {"retain_fixed_regression", "pairwise_replaces_fixed", "fixed_row"}, "incorrect decision fields")
        boolean(plan, "retain_fixed_regression", True)
        boolean(plan, "pairwise_replaces_fixed", False)
        require(plan["fixed_row"] == ["Safari", "PNG", "custom font", "transparent background"], "wrong mandatory row")
    elif fixture.startswith("e61-"):
        require(set(plan) == {"business_rule_tier", "integration_contracts", "browser_role", "retry_action", "first_action"}, "incorrect decision fields")
        require(plan["business_rule_tier"] in {"domain", "service", "api"}, "business rules still require a browser")
        boolean(plan, "integration_contracts", True)
        require(plan["browser_role"] == "wiring_and_core_journeys", "browser coverage was deleted or expanded for rules")
        require(plan["retry_action"] == "diagnose_not_increase" and plan["first_action"] == "move_rule_tests", "first fix is more browser work or retry masking")
    elif fixture.startswith("e57-"):
        require(set(plan) == {"computed_expectation", "shared_mutable_state", "setup_location", "expectation_source"}, "incorrect decision fields")
        boolean(plan, "computed_expectation", True)
        boolean(plan, "shared_mutable_state", True)
        require(plan["setup_location"] == "per_behavior" and plan["expectation_source"] == "specified_literals", "retains coupled setup or mirrored expectations")
    elif fixture.startswith("e58-"):
        require(set(plan) == {"retain_whole_state", "quota_only_replacement", "contract"}, "incorrect decision fields")
        boolean(plan, "retain_whole_state", True)
        boolean(plan, "quota_only_replacement", False)
        require(plan["contract"] == "save_load_identity", "wrong roundtrip contract")
    else:
        raise ValueError(f"unsupported decision fixture: {fixture}")


def check_output(fixture: str, output: Path) -> None:
    require(output.stat().st_size <= 128 * 1024, "output exceeds 128 KiB")
    check(fixture, output.read_text(encoding="utf-8"))


def main(fixture: str) -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    try:
        files = sorted(root.rglob("*.md"))
        require(0 < len(files) <= 10, "expected 1 to 10 Markdown candidate files")
        require(all(not file.is_symlink() and file.resolve().is_relative_to(root.resolve()) for file in files), "candidate file escapes output directory")
        require(sum(file.stat().st_size for file in files) <= 128 * 1024, "output exceeds 128 KiB")
        check(fixture, "\n".join(file.read_text(encoding="utf-8") for file in files))
    except (OSError, UnicodeError, ValueError, TypeError, KeyError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print("PASS: requested decision fields only (data-only; candidate code not executed)")
    return 0
