#!/usr/bin/env python3
"""Before/after prompt-eval runner for the testing-best-practices skill.

Pipeline per eval: (1) obtain a candidate answer, (2) if the eval has a fixture
oracle, run it against the produced files (objective pass/fail), (3) if a judge
backend is given, score the rubric dimensions in the eval's ``rubric_focus``
against ``evals/rubric.md`` (eval score = min of dims, 0 on critical-failure
override). Producing the candidate and judging are *pluggable backends* -- a
Claude Code sub-agent, ``claude -p`` headless, or a raw API call all work. The
runner itself never calls a model; it orchestrates whatever backend you point
it at and owns the deterministic oracle + score arithmetic.

Generation backends
--------------------
- ``--candidate-dir DIR``  Score an already-produced candidate. This is the
  sub-agent path: spawn a sub-agent that writes the answer file(s) into DIR,
  then run with ``--candidate-dir DIR``.
- ``--agent-cmd "CMD"``    Generate by shelling out. The prompt is passed on
  stdin and ``{dir}`` / ``{prompt_file}`` are substituted; cwd = candidate dir.
  Example: ``--agent-cmd 'claude -p --permission-mode acceptEdits'``
- (neither)                Stage the run dir + prompt and print the manual /
  sub-agent instructions, then stop before scoring.

Judge backend
-------------
- ``--judge-cmd "CMD"``    Score the candidate against the rubric. The judge
  prompt is passed on stdin; the command must print a JSON object
  ``{"dimensions": {"C": 0-4, ...}, "critical_failure": bool, "rationale": ...}``
  scoring only the eval's rubric_focus dims. Example: ``--judge-cmd 'claude -p'``.
  Without it, rubric scores stay provisional (per rubric.md rule 4).

Evals with no fixture (e.g. hidden probes) are judge-only and need ``--judge-cmd``.

Not part of ``check-all.py``: it depends on a model, so it is not a
deterministic gate. The fixture-oracle self-tests in ``run-fixture-oracles.py``
remain the non-LLM gate. Run artifacts land in the gitignored ``eval-runs/``.

Stdlib-only by design.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALS = ROOT / "evals" / "evals.json"
FIXTURES = ROOT / "evals" / "fixtures"
RUBRIC = ROOT / "evals" / "rubric.md"
RUNS = ROOT / "eval-runs"  # gitignored

CODE_GLOBS = ("*.py", "*.ts", "*.tsx", "*.js", "*.go", "*.rs")


def load_evals() -> list[dict]:
    return json.loads(EVALS.read_text())["evals"]


def fixture_for(eval_id: str) -> Path | None:
    """Map an eval id (E33-...) to its fixture dir (e33-...)."""
    prefix = eval_id.split("-", 1)[0].lower()  # "E33-..." -> "e33"
    matches = sorted(FIXTURES.glob(f"{prefix}-*"))
    return matches[0] if matches and (matches[0] / "manifest.json").exists() else None


def run_oracle(fixture: Path, candidate_dir: Path) -> tuple[bool, str]:
    manifest = json.loads((fixture / "manifest.json").read_text())
    oracle = fixture / manifest["oracle"]
    # The oracle runs with cwd=fixture, so the candidate path must be absolute.
    proc = subprocess.run(
        [sys.executable, str(oracle), str(candidate_dir.resolve())],
        cwd=fixture, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    return proc.returncode == 0, (proc.stdout + proc.stderr).strip()


def generate(agent_cmd: str, prompt: str, prompt_file: Path, candidate_dir: Path) -> int:
    cmd = agent_cmd.replace("{dir}", str(candidate_dir)).replace("{prompt_file}", str(prompt_file))
    print(f"  $ {cmd}  (cwd={candidate_dir}, prompt on stdin)")
    return subprocess.run(cmd, shell=True, cwd=candidate_dir, input=prompt, text=True).returncode


def read_candidate(candidate_dir: Path) -> str:
    parts = []
    for pattern in CODE_GLOBS:
        for p in sorted(candidate_dir.rglob(pattern)):
            parts.append(f"# ---- {p.relative_to(candidate_dir)} ----\n{p.read_text(errors='ignore')}")
    return "\n\n".join(parts)


def build_judge_prompt(ev: dict, prompt: str, candidate_text: str) -> str:
    focus = ev.get("rubric_focus", [])
    return (
        f"{RUBRIC.read_text()}\n\n"
        "---\nYou are grading one prompt eval. Score ONLY these rubric dimensions: "
        f"{focus}. Use the 0-4 scale and the critical-failure overrides above.\n\n"
        f"## Eval task prompt\n{prompt}\n\n"
        f"## Expected behavior\n{json.dumps(ev.get('expected_behavior', []), indent=2)}\n\n"
        f"## Red flags\n{json.dumps(ev.get('red_flags', []), indent=2)}\n\n"
        f"## Candidate answer (files produced)\n```\n{candidate_text}\n```\n\n"
        "Respond with ONLY a JSON object, no prose, of the form:\n"
        '{"dimensions": {' + ", ".join(f'"{d}": <0-4>' for d in focus) + '}, '
        '"critical_failure": <true|false>, "rationale": "<= 2 sentences"}'
    )


def run_judge(judge_cmd: str, judge_prompt: str) -> str:
    return subprocess.run(judge_cmd, shell=True, input=judge_prompt, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout


def parse_judge(stdout: str) -> dict | None:
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", stdout, re.DOTALL)
    blob = fence.group(1) if fence else None
    if blob is None:  # fall back to first balanced {...}
        start = stdout.find("{")
        if start == -1:
            return None
        depth = 0
        for i in range(start, len(stdout)):
            depth += (stdout[i] == "{") - (stdout[i] == "}")
            if depth == 0:
                blob = stdout[start:i + 1]
                break
    try:
        return json.loads(blob) if blob else None
    except json.JSONDecodeError:
        return None


def judge_score(ev: dict, parsed: dict) -> tuple[float | None, bool]:
    focus = ev.get("rubric_focus", [])
    dims = parsed.get("dimensions", {})
    vals = [dims[d] for d in focus if isinstance(dims.get(d), (int, float))]
    if len(vals) != len(focus):
        return None, False  # judge omitted a dimension; treat as unscored
    if parsed.get("critical_failure"):
        return 0.0, True
    return float(min(vals)), False


def score_one(ev: dict, fixture: Path | None, run_dir: Path, agent_cmd: str | None,
              candidate_dir: Path | None, judge_cmd: str | None) -> dict:
    prompt = ev["prompt"]
    if fixture and (fixture / "prompt.md").exists():
        prompt = (fixture / "prompt.md").read_text()

    if candidate_dir is None:
        candidate_dir = run_dir / "candidate"
        candidate_dir.mkdir(parents=True, exist_ok=True)
        prompt_file = run_dir / "prompt.md"
        prompt_file.write_text(prompt)
        if agent_cmd:
            rc = generate(agent_cmd, prompt, prompt_file, candidate_dir)
            if rc != 0:
                print(f"  ! agent-cmd exited {rc}", file=sys.stderr)
        else:
            print("\n  [manual / sub-agent backend]")
            print(f"  Have a sub-agent answer the prompt and write file(s) into:\n    {candidate_dir}")
            print(f"  Prompt written to: {prompt_file}")
            print(f"  Then re-run with: --eval {ev['id']} --candidate-dir {candidate_dir}"
                  + (" --judge-cmd '...'" if not fixture else "") + "\n")
            return {"id": ev["id"], "status": "awaiting-candidate", "candidate_dir": str(candidate_dir)}

    res: dict = {
        "id": ev["id"],
        "fixture": fixture.name if fixture else None,
        "candidate_dir": str(candidate_dir),
        "rubric_focus": ev.get("rubric_focus", []),
        "critical": ev.get("critical", False),
        "oracle_pass": None,
        "rubric_scores": {dim: None for dim in ev.get("rubric_focus", [])},
        "score": None,
        "provisional": True,
    }
    if fixture:
        ok, detail = run_oracle(fixture, candidate_dir)
        res["oracle_pass"], res["oracle_detail"] = ok, detail

    if judge_cmd:
        candidate_text = read_candidate(candidate_dir)
        jp = build_judge_prompt(ev, prompt, candidate_text)
        (run_dir / "judge-prompt.txt").write_text(jp)
        out = run_judge(judge_cmd, jp)
        (run_dir / "judge-output.txt").write_text(out)
        parsed = parse_judge(out)
        if parsed is None:
            res["judge_error"] = "could not parse judge JSON (see judge-output.txt)"
        else:
            score, critical = judge_score(ev, parsed)
            res["rubric_scores"] = parsed.get("dimensions", res["rubric_scores"])
            res["judge_rationale"] = parsed.get("rationale")
            res["judge_critical_failure"] = critical
            res["score"] = score
            # Backed by a saved transcript (+ oracle when present) -> not provisional.
            res["provisional"] = score is None
    return res


def print_result(res: dict) -> None:
    if res.get("status") == "awaiting-candidate":
        return
    print(f"\n=== {res['id']} ===")
    if res["oracle_pass"] is not None:
        mark = "PASS" if res["oracle_pass"] else "FAIL"
        print(f"  fixture oracle: {mark}")
        if not res["oracle_pass"]:
            print(f"    -> {res['oracle_detail']}")
    else:
        print("  fixture oracle: (none -- judge-only eval)")
    print(f"  rubric dims (min, see rubric.md): {res['rubric_focus']}")
    if res.get("judge_error"):
        print(f"  judge: ERROR -- {res['judge_error']}")
    elif res["score"] is not None:
        flag = "  [CRITICAL-FAILURE OVERRIDE -> 0]" if res.get("judge_critical_failure") else ""
        print(f"  rubric scores: {res['rubric_scores']}")
        print(f"  eval score: {res['score']}/4{flag}  (backed by transcript)")
        if res.get("judge_rationale"):
            print(f"  rationale: {res['judge_rationale']}")
    else:
        print("  rubric scores: provisional (no judge backend run)")
    print(f"  candidate: {res['candidate_dir']}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true", help="list evals and whether each has a fixture oracle")
    ap.add_argument("--eval", help="eval id to run")
    ap.add_argument("--candidate-dir", help="score an already-produced candidate dir (sub-agent path)")
    ap.add_argument("--agent-cmd", help="shell command to generate the candidate; {dir}/{prompt_file} substituted, prompt on stdin")
    ap.add_argument("--judge-cmd", help="shell command that reads a judge prompt on stdin and prints rubric-score JSON")
    args = ap.parse_args()

    evals = load_evals()

    if args.list or not args.eval:
        print(f"evals: {len(evals)}")
        for ev in evals:
            fx = fixture_for(ev["id"])
            tag = f"fixture={fx.name}" if fx else "judge-only"
            hidden = " [hidden]" if ev.get("hidden") else ""
            print(f"  {ev['id']:<45} {tag:<40} rubric={ev.get('rubric_focus')}{hidden}")
        if not args.eval:
            print("\nRun one with: --eval <id> [--candidate-dir DIR | --agent-cmd 'CMD'] [--judge-cmd 'CMD']")
        return 0

    match = next((e for e in evals if e["id"] == args.eval), None)
    if match is None:
        print(f"unknown eval id: {args.eval}", file=sys.stderr)
        return 2
    fixture = fixture_for(match["id"])
    if fixture is None and not (args.judge_cmd or args.candidate_dir):
        print(f"{match['id']} has no fixture oracle; it is judge-only. "
              f"Provide --judge-cmd (and produce a candidate) to score it.", file=sys.stderr)

    stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = RUNS / stamp / match["id"]
    run_dir.mkdir(parents=True, exist_ok=True)
    candidate_dir = Path(args.candidate_dir) if args.candidate_dir else None

    res = score_one(match, fixture, run_dir, args.agent_cmd, candidate_dir, args.judge_cmd)
    print_result(res)
    (run_dir / "result.json").write_text(json.dumps(res, indent=2))
    print(f"\nresult: {run_dir / 'result.json'}")
    if res.get("status") == "awaiting-candidate":
        return 0
    if res["oracle_pass"] is False:
        return 1
    if res["score"] is not None and res["score"] < 3:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
