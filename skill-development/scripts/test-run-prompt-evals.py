#!/usr/bin/env python3
"""Regression checks for prompt-eval ingestion, framing, and fail-closed scoring."""
from __future__ import annotations

import importlib.util
import json
import shlex
import sys
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).with_name("run-prompt-evals.py")
SPEC = importlib.util.spec_from_file_location("run_prompt_evals", SCRIPT)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - import contract
    raise RuntimeError(f"cannot load {SCRIPT}")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def check_candidate_ingestion_and_framing() -> None:
    assessment = """Assessment

```python
assert parser(b"input") == expected
```

The literal ```` token must remain inside the candidate.
"""
    with tempfile.TemporaryDirectory() as tmp:
        candidate_dir = Path(tmp)
        (candidate_dir / "assessment.md").write_text(assessment)
        candidate = MODULE.read_candidate(candidate_dir)

    assert "# ---- assessment.md ----" in candidate
    assert assessment in candidate

    ev = {"rubric_focus": ["B"], "expected_behavior": [], "red_flags": []}
    judge_prompt = MODULE.build_judge_prompt(ev, "Audit the test.", candidate)
    fence = MODULE.markdown_fence(candidate)
    assert len(fence) > 4
    framed = f"## Candidate answer (files produced)\n{fence}\n{candidate}\n{fence}\n\n"
    assert framed in judge_prompt
    assert "\n```python\n" in judge_prompt


def check_judge_schema() -> None:
    ev = {"rubric_focus": ["B", "C"]}
    assert MODULE.judge_score(
        ev,
        {"dimensions": {"B": 4, "C": 3}, "critical_failure": False},
    ) == (3.0, False)
    assert MODULE.judge_score(
        ev,
        {"dimensions": {"B": 4, "C": 4}, "critical_failure": True},
    ) == (0.0, True)

    invalid = [
        {"dimensions": {"B": 4}, "critical_failure": False},
        {"dimensions": {"B": 4, "C": 5}, "critical_failure": False},
        {"dimensions": {"B": 4, "C": True}, "critical_failure": False},
        {"dimensions": {"B": 4, "C": 3}},
    ]
    for result in invalid:
        assert MODULE.judge_score(ev, result) == (None, False)


def check_fail_closed_exit_codes() -> None:
    assert MODULE.result_exit_code({"status": "awaiting-candidate"}, False) == 0
    assert MODULE.result_exit_code({"status": "generation-failed"}, False) == 1
    assert MODULE.result_exit_code({"oracle_pass": False, "score": None}, False) == 1
    assert MODULE.result_exit_code({"oracle_pass": None, "score": None}, False) == 1
    assert MODULE.result_exit_code({"oracle_pass": True, "score": None}, False) == 0
    assert MODULE.result_exit_code({"oracle_pass": True, "score": None}, True) == 1
    assert MODULE.result_exit_code({"oracle_pass": True, "score": 2.0}, True) == 1
    assert MODULE.result_exit_code({"oracle_pass": True, "score": 3.0}, True) == 0


def check_generation_failure() -> None:
    original_generate = MODULE.generate
    MODULE.generate = lambda *_args: 7
    try:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            with redirect_stderr(StringIO()):
                result = MODULE.score_one(
                    {"id": "example", "prompt": "Write tests."},
                    fixture=None,
                    run_dir=run_dir,
                    agent_cmd="unused",
                    candidate_dir=None,
                    judge_cmd=None,
                )
    finally:
        MODULE.generate = original_generate
    assert result["status"] == "generation-failed"
    assert result["generation_exit_code"] == 7
    assert MODULE.result_exit_code(result, judge_requested=False) == 1


def check_judge_process_status() -> None:
    eval_id = "E75-generic-exit-status-not-output"
    fixture = MODULE.fixture_for(eval_id)
    assert fixture is not None
    dimensions = {"H": 4}  # Rubric H is output and validation honesty.
    grade = json.dumps({"dimensions": dimensions, "critical_failure": False, "rationale": "stub"})
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        runs = root / "runs"
        judge = root / "judge.py"
        judge.write_text(
            "import sys\n"
            "print(sys.argv[1])\n"
            "print('backend diagnostic', file=sys.stderr)\n"
            "sys.exit(int(sys.argv[2]))\n"
        )
        exits = []
        reports = []
        with patch.object(MODULE, "RUNS", runs), patch.object(MODULE._dt, "datetime") as clock:
            clock.now.return_value = datetime(2026, 1, 1, tzinfo=timezone.utc)
            for code in (0, 7):
                command = shlex.join([sys.executable, str(judge), grade, str(code)])
                args = [str(SCRIPT), "--eval", eval_id, "--candidate-dir", str(fixture / "samples/good"),
                        "--judge-cmd", command]
                with patch.object(sys, "argv", args), redirect_stdout(StringIO()) as output:
                    exits.append(MODULE.main())
                    reports.append(output.getvalue())
        assert exits == [0, 1], f"CLI exits for judge success/failure: {exits}"
        assert "4.0/4" in reports[0]
        assert "provisional" in reports[1] and "4.0/4" not in reports[1]
        results = {}
        for path in runs.rglob("result.json"):
            result = json.loads(path.read_text())
            assert result["oracle_pass"] is True
            assert (path.parent / "judge-output.txt").read_text().strip() == grade
            assert (path.parent / "judge-stderr.txt").read_text().strip() == "backend diagnostic"
            results[result["judge_exit_code"]] = result
        assert results[0]["score"] == 4.0 and results[0]["provisional"] is False
        assert results[7]["score"] is None and results[7]["provisional"] is True
        assert results[7]["rubric_scores"] == dict.fromkeys(dimensions)
        assert "7" in results[7]["judge_error"]


def check_oracle_process_status() -> None:
    eval_id = "E75-generic-exit-status-not-output"
    grade = '{"dimensions": {"H": 4}, "critical_failure": false}'
    judge = shlex.join([sys.executable, "-c", f"print({grade!r})"])
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        fixture = root / "fixtures/e75-test"
        fixture.mkdir(parents=True)
        (fixture / "oracle.py").write_text(
            "import sys\nfrom pathlib import Path\n"
            "code = int(Path(sys.argv[1]).name)\n"
            "print(f'oracle diagnostic {code}', file=sys.stderr)\n"
            "sys.exit(code)\n"
        )
        for code, reserved in [(2, [2]), (1, [2]), (2, [])]:
            manifest = {"oracle": "oracle.py"}
            if reserved:
                manifest["unavailable_exit_codes"] = reserved
            (fixture / "manifest.json").write_text(json.dumps(manifest))
            candidate = root / str(code)
            candidate.mkdir(exist_ok=True)
            (candidate / "answer.md").write_text("candidate answer")
            runs = root / f"runs-{code}-{bool(reserved)}"
            args = [str(SCRIPT), "--eval", eval_id, "--candidate-dir", str(candidate), "--judge-cmd", judge]
            with patch.object(MODULE, "FIXTURES", fixture.parent), patch.object(MODULE, "RUNS", runs), \
                 patch.object(sys, "argv", args), redirect_stdout(StringIO()) as output:
                assert MODULE.main() == 1
            result_path, = runs.rglob("result.json")
            result = json.loads(result_path.read_text())
            assert result["judge_exit_code"] == 0
            assert (result_path.parent / "judge-output.txt").read_text().strip() == grade
            assert result["oracle_detail"] == f"oracle diagnostic {code}"
            if code in reserved:
                assert result["oracle_pass"] is None, result
                assert result["oracle_status"] == "unavailable" and result["oracle_error"]
                assert result["score"] is None and result["provisional"] is True
                assert result["rubric_scores"] == {"H": None}
                assert "fixture oracle: UNAVAILABLE" in output.getvalue()
                assert "oracle diagnostic 2" in output.getvalue()
                assert "judge-only" not in output.getvalue()
            else:
                assert result["oracle_pass"] is False and result["oracle_status"] == "failed"
                assert "oracle_error" not in result
                assert result["score"] == 4.0 and result["provisional"] is False
                assert "fixture oracle: FAIL" in output.getvalue()
            assert result["oracle_exit_code"] == code


def check_empty_candidate_fails_before_judging() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        candidate_dir = root / "candidate"
        candidate_dir.mkdir()
        result = MODULE.score_one(
            {"id": "example", "prompt": "Assess tests.", "rubric_focus": ["C"]},
            fixture=None,
            run_dir=root,
            agent_cmd=None,
            candidate_dir=candidate_dir,
            judge_cmd="must-not-run",
        )
    assert result["judge_error"] == "no supported candidate files found"
    assert MODULE.result_exit_code(result, judge_requested=True) == 1


def main() -> int:
    check_candidate_ingestion_and_framing()
    check_judge_schema()
    check_fail_closed_exit_codes()
    check_generation_failure()
    check_judge_process_status()
    check_oracle_process_status()
    check_empty_candidate_fails_before_judging()
    print("OK: prompt-eval runner collects complete candidates and fails closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
