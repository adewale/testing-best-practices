#!/usr/bin/env python3
"""Before/after prompt-eval runner for the testing-best-practices skill.

The deterministic core of this runner is: (1) obtain a candidate answer for an
eval prompt, (2) run that eval's fixture oracle against the produced files, and
(3) surface the rubric dimensions a judge must score. Producing the candidate
answer is a *pluggable backend* -- a Claude Code sub-agent, `claude -p`
headless, or a raw API call all work. The runner itself never calls a model; it
orchestrates whatever backend you point it at and owns the objective scoring.

Backends
--------
- ``--candidate-dir DIR``  Score an already-produced candidate. This is the
  sub-agent path: spawn a sub-agent that writes the test file(s) into DIR, then
  run this with ``--candidate-dir DIR`` to get the oracle verdict + scorecard.
- ``--agent-cmd "CMD"``    Generate the candidate by shelling out. The prompt is
  passed on stdin and ``{dir}`` / ``{prompt_file}`` are substituted. The command
  runs with cwd = the candidate dir, so it should write test files there.
  Example: ``--agent-cmd 'claude -p --permission-mode acceptEdits'``
- (neither)                Materialize the run dir + prompt and print the
  manual/sub-agent instructions, then stop before scoring.

This is intentionally NOT part of ``check-all.py``: it depends on a model, so it
is not a deterministic gate. Use it to produce scorecard evidence; the fixture
oracle self-tests in ``run-fixture-oracles.py`` remain the non-LLM gate.

Stdlib-only by design.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALS = ROOT / "evals" / "evals.json"
FIXTURES = ROOT / "evals" / "fixtures"
RUBRIC = ROOT / "evals" / "rubric.md"
RUNS = ROOT / "eval-runs"  # gitignored


def load_evals() -> list[dict]:
    return json.loads(EVALS.read_text())["evals"]


def fixture_for(eval_id: str) -> Path | None:
    """Map an eval id (E33-...) to its fixture dir (e33-...)."""
    prefix = eval_id.split("-", 1)[0].lower()  # "E33-..." -> "e33"
    matches = sorted(FIXTURES.glob(f"{prefix}-*"))
    return matches[0] if matches and (matches[0] / "manifest.json").exists() else None


def runnable_evals(evals: list[dict]) -> list[tuple[dict, Path]]:
    out = []
    for ev in evals:
        fx = fixture_for(ev["id"])
        if fx:
            out.append((ev, fx))
    return out


def run_oracle(fixture: Path, candidate_dir: Path) -> tuple[bool, str]:
    manifest = json.loads((fixture / "manifest.json").read_text())
    oracle = fixture / manifest["oracle"]
    # The oracle runs with cwd=fixture, so the candidate path must be absolute.
    proc = subprocess.run(
        [sys.executable, str(oracle), str(candidate_dir.resolve())],
        cwd=fixture, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    detail = (proc.stdout + proc.stderr).strip()
    return proc.returncode == 0, detail


def generate(agent_cmd: str, prompt: str, prompt_file: Path, candidate_dir: Path) -> int:
    cmd = agent_cmd.replace("{dir}", str(candidate_dir)).replace("{prompt_file}", str(prompt_file))
    print(f"  $ {cmd}  (cwd={candidate_dir}, prompt on stdin)")
    proc = subprocess.run(cmd, shell=True, cwd=candidate_dir, input=prompt, text=True)
    return proc.returncode


def score_one(ev: dict, fixture: Path, run_dir: Path, agent_cmd: str | None,
              candidate_dir: Path | None) -> dict:
    prompt = (fixture / "prompt.md").read_text() if (fixture / "prompt.md").exists() else ev["prompt"]
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
            print(f"\n  [manual / sub-agent backend]")
            print(f"  Have a sub-agent answer the prompt and write test file(s) into:")
            print(f"    {candidate_dir}")
            print(f"  Prompt written to: {prompt_file}")
            print(f"  Then re-run with: --eval {ev['id']} --candidate-dir {candidate_dir}\n")
            return {"id": ev["id"], "status": "awaiting-candidate", "candidate_dir": str(candidate_dir)}

    ok, detail = run_oracle(fixture, candidate_dir)
    return {
        "id": ev["id"],
        "fixture": fixture.name,
        "candidate_dir": str(candidate_dir),
        "oracle_pass": ok,
        "oracle_detail": detail,
        "rubric_focus": ev.get("rubric_focus", []),
        "critical": ev.get("critical", False),
        # min-of-dimensions per rubric.md; provisional until a judge fills these in.
        "rubric_scores": {dim: None for dim in ev.get("rubric_focus", [])},
        "score": None,
        "provisional": True,
    }


def print_result(res: dict) -> None:
    if res.get("status") == "awaiting-candidate":
        return
    mark = "PASS" if res["oracle_pass"] else "FAIL"
    print(f"\n=== {res['id']} ===")
    print(f"  fixture oracle: {mark}")
    if not res["oracle_pass"]:
        print(f"    -> {res['oracle_detail']}")
    print(f"  rubric dims to judge (score = min, see evals/rubric.md): {res['rubric_focus']}")
    print(f"  candidate: {res['candidate_dir']}")
    print(f"  rubric scores: provisional (no judge backend run)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true", help="list evals with a runnable fixture oracle")
    ap.add_argument("--eval", help="eval id to run (e.g. E33-python-fault-injection-error-paths)")
    ap.add_argument("--candidate-dir", help="score an already-produced candidate dir (sub-agent path)")
    ap.add_argument("--agent-cmd", help="shell command to generate the candidate; {dir}/{prompt_file} substituted, prompt on stdin")
    args = ap.parse_args()

    evals = load_evals()

    if args.list or not args.eval:
        runnable = runnable_evals(evals)
        print(f"runnable prompt evals (have a fixture oracle): {len(runnable)}/{len(evals)}")
        for ev, fx in runnable:
            print(f"  {ev['id']:<45} fixture={fx.name}  rubric={ev.get('rubric_focus')}")
        if not args.eval:
            print("\nRun one with: --eval <id> [--candidate-dir DIR | --agent-cmd 'CMD']")
        return 0

    match = next((e for e in evals if e["id"] == args.eval), None)
    if match is None:
        print(f"unknown eval id: {args.eval}", file=sys.stderr)
        return 2
    fixture = fixture_for(match["id"])
    if fixture is None:
        print(f"{match['id']} has no fixture oracle; not runnable end-to-end", file=sys.stderr)
        return 2

    stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = RUNS / stamp / match["id"]
    run_dir.mkdir(parents=True, exist_ok=True)
    candidate_dir = Path(args.candidate_dir) if args.candidate_dir else None

    res = score_one(match, fixture, run_dir, args.agent_cmd, candidate_dir)
    print_result(res)
    (run_dir / "result.json").write_text(json.dumps(res, indent=2))
    print(f"\nresult: {run_dir / 'result.json'}")
    if res.get("status") == "awaiting-candidate":
        return 0
    return 0 if res["oracle_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
