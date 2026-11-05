#!/usr/bin/env python3
"""Self-test data-only decisions and static-only untrusted candidate grading."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHARED = ROOT / "evals/oracles/development_fixture_oracle.py"
FIXTURE = ROOT / "skill-development/evals/fixtures/e67-combinatorial-registry-sabotage/oracle.py"
SAMPLES = ROOT / "skill-development/evals/fixtures/e67-combinatorial-registry-sabotage/samples"
GOOD = SAMPLES / "good"

DECISIONS = {
    "e57-python-damp-shared-fixture": {
        "computed_expectation": True, "shared_mutable_state": True,
        "setup_location": "per_behavior", "expectation_source": "specified_literals",
    },
    "e58-hidden-narrow-not-roundtrip": {
        "retain_whole_state": True, "quota_only_replacement": False,
        "contract": "save_load_identity",
    },
    "e61-suite-shape-assess": {
        "business_rule_tier": "domain", "integration_contracts": True,
        "browser_role": "wiring_and_core_journeys", "retry_action": "diagnose_not_increase",
        "first_action": "move_rule_tests",
    },
    "e64-mutation-recurring-lane-contract": {
        "schedule_now": False, "score_floor": None, "scope": "changed_code",
        "fits_single_runner": False, "missing_evidence": ["completed_baseline", "fault_class_bite", "owner"],
    },
    "e65-mutation-survivor-triage": {
        "restore_70_percent": False,
        "rows": [{"id": key, "classification": value} for key, value in [
            ("A", "actionable_survivor"), ("B", "equivalent_survivor"), ("C", "timeout"),
            ("D", "compile_failure"), ("E", "no_coverage"),
            ("F", "infrastructure_failure"), ("G", "unobserved"),
        ]],
    },
    "e66-combinatorial-cost-aware-portfolio": {
        "registry_source": "production_registry", "cheap_slices": "exhaustive",
        "base_matrix": "constrained_pairwise", "elevated_group": ["family", "look", "palette"],
        "retain_fixed_regression": True, "delete_before_comparison": False,
        "costs": ["runtime", "setup", "triage"],
    },
    "e68-hidden-mutation-valid-recurring-lane": {
        "approve": True, "scope": "changed_authorization_predicate", "aggregate_score_floor": None,
        "timeout_seconds": 300, "owner": "security_team", "expiry_days": 90,
    },
    "e69-hidden-combinatorial-known-high-order-regression": {
        "retain_fixed_regression": True, "pairwise_replaces_fixed": False,
        "fixed_row": ["Safari", "PNG", "custom font", "transparent background"],
    },
}


def shared_command(fixture: str, candidate: Path) -> list[str]:
    manifest = json.loads((ROOT / "evals/shared-benchmark.json").read_text())
    commands = [assertion["command"] for case in manifest["cases"]
                for assertion in case.get("assertions", [])
                if assertion.get("type") == "script" and fixture in assertion.get("command", [])]
    assert len(commands) == 1, f"expected one shared assertion for {fixture}"
    command = commands[0]
    assert command[:2] == ["python3", "oracles/development_fixture_oracle.py"]
    return [sys.executable, str(ROOT / "evals" / command[1]),
            *[str(candidate) if arg == "{output_dir}" else arg for arg in command[2:]]]


def test_decisions(root: Path) -> None:
    spec = importlib.util.spec_from_file_location("decision_checks", ROOT / "evals/oracles/decision_vectors.py")
    assert spec is not None and spec.loader is not None
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    controls = 0
    for fixture, good in DECISIONS.items():
        def render(plan: dict) -> str:
            return "```json\n" + json.dumps(plan) + "\n```\n"

        checker.check(fixture, render(good))
        candidate = root / fixture
        candidate.mkdir()
        output = candidate / "output.md"
        output.write_text(render(good))
        run(shared_command(fixture, candidate))

        def reject(text: str, fixture: str = fixture) -> None:
            nonlocal controls
            try:
                checker.check(fixture, text)
            except (ValueError, TypeError):
                controls += 1
            else:
                raise AssertionError(f"incorrect decision accepted for {fixture}: {text}")

        # Each field is tested with all the other fields still correct, so the
        # intended rule is reached instead of failing at JSON parsing first.
        for key, value in good.items():
            bad = dict(good)
            bad[key] = not value if type(value) is bool else "wrong"
            reject(render(bad))
            missing = dict(good)
            del missing[key]
            reject(render(missing))
        prompt = ROOT / "skill-development/evals/fixtures" / fixture / "prompt.md"
        reject(prompt.read_text())
        keyword_salad = "baseline owner timeout contract survivor regression pairwise cost domain integration"
        reject(keyword_salad)
        reject(render(good) + render(good))
        reject('{"not": "a fence"}')
        first_key = next(iter(good))
        duplicated = render(good).replace("{", '{"' + first_key + '": null,', 1)
        reject(duplicated)
        reject("x" * (128 * 1024 + 1))
        # A sibling case's correct decision is not evidence for this case.
        sibling = next(plan for name, plan in DECISIONS.items() if name != fixture)
        reject(render(sibling))
        output.write_text(keyword_salad)
        run_rejected(shared_command(fixture, candidate))

    # Exercise enrollment/status omissions and type confusion independently.
    for replacement in [[], DECISIONS["e65-mutation-survivor-triage"]["rows"][:-1]]:
        bad = dict(DECISIONS["e65-mutation-survivor-triage"], rows=replacement)
        try:
            checker.check("e65-mutation-survivor-triage", render(bad))
        except ValueError:
            controls += 1
        else:
            raise AssertionError("incomplete report passed")
    print(f"OK: {len(DECISIONS)} data-only decision cases; {controls} independent negative controls")


def run(command: list[str], *, trusted_fixture_flag: bool = False) -> None:
    env = os.environ.copy()
    if trusted_fixture_flag:
        env["TBP_TRUSTED_FIXTURE_SELF_TEST"] = "1"
    proc = subprocess.run(command, text=True, capture_output=True, env=env)
    if proc.returncode:
        raise AssertionError(f"command failed: {command}\nstdout={proc.stdout}\nstderr={proc.stderr}")


def run_rejected(command: list[str]) -> None:
    proc = subprocess.run(command, text=True, capture_output=True)
    if proc.returncode == 0:
        raise AssertionError(f"invalid candidate passed: {command}\nstdout={proc.stdout}\nstderr={proc.stderr}")


def test_e60_static_only(root: Path) -> None:
    fixture = ROOT / "skill-development/evals/fixtures/e60-python-fake-contract-weld"
    candidate = root / "e60-untrusted"
    candidate.mkdir()
    marker = root / "E60_MODEL_CODE_EXECUTED"
    good = (fixture / "samples/good/test_store_contract.py").read_text()
    poison = f"from pathlib import Path\nPath({str(marker)!r}).write_text('unsafe')\n" + good
    (candidate / "test_contract.py").write_text(poison)
    command = [sys.executable, str(fixture / "oracle.py"), str(candidate)]
    run(command)
    run(command, trusted_fixture_flag=True)
    assert not marker.exists(), "E60 executed untrusted code through a local/ambient trusted flag"
    shared = root / "e60-shared"
    shared.mkdir()
    (shared / "output.md").write_text("```python\n" + poison + "\n```\n")
    run([sys.executable, str(ROOT / "evals/oracles/gtb_output_adapter.py"), str(shared), fixture.name])
    assert not marker.exists(), "E60 shared grading executed untrusted code"
    for name in ("bad-fixture-override", "bad-renamed-fixture"):
        invalid = (fixture / "samples" / name / "test_store_contract.py").read_text()
        (shared / "output.md").write_text("```python\n" + invalid + "\n```\n")
        run_rejected([sys.executable, str(ROOT / "evals/oracles/gtb_output_adapter.py"), str(shared), fixture.name])
    print("OK: E60 shared/local grading never executes candidate Python")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="tbp-untrusted-oracle-") as directory:
        root = Path(directory)
        test_decisions(root)
        test_e60_static_only(root)
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
        run([sys.executable, str(FIXTURE), str(candidate)], trusted_fixture_flag=True)
        assert not marker.exists(), "ambient trusted-fixture flag executed an untrusted candidate path"

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

        for sample_name in ("bad-partial-owner", "bad-toothless-contract"):
            sample = SAMPLES / sample_name
            rejected = root / f"shared-{sample_name}"
            rejected.mkdir()
            rejected.joinpath("output.md").write_text(
                f"portfolio.py\n```python\n{sample.joinpath('portfolio.py').read_text()}\n```\n"
                f"test_portfolio.py\n```python\n{sample.joinpath('test_portfolio.py').read_text()}\n```\n"
            )
            run_rejected([
                sys.executable,
                str(SHARED),
                "e67-combinatorial-registry-sabotage",
                str(rejected),
            ])

    print("OK: E67 shared/local candidate grading is static-only and fails closed on partial/vacuous cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
