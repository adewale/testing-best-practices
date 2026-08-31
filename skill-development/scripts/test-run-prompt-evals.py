#!/usr/bin/env python3
"""Regression checks for prompt-eval candidate ingestion and framing."""
from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).with_name("run-prompt-evals.py")
SPEC = importlib.util.spec_from_file_location("run_prompt_evals", SCRIPT)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - import contract
    raise RuntimeError(f"cannot load {SCRIPT}")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def main() -> int:
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
    print("OK: Markdown candidates are collected and safely fenced")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
