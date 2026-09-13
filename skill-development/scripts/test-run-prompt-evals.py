#!/usr/bin/env python3
"""Regression checks for prompt-eval ingestion, framing, and fail-closed scoring."""
from __future__ import annotations

import importlib.util
import tempfile
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path

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
    check_empty_candidate_fails_before_judging()
    print("OK: prompt-eval runner collects complete candidates and fails closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
