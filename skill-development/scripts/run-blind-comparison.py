#!/usr/bin/env python3
"""Run blinded Skill Eval Harness comparison tasks through a Pi judge."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def parse_json(text: str) -> dict:
    decoder = json.JSONDecoder()
    start = text.find("{")
    while start >= 0:
        try:
            value, _ = decoder.raw_decode(text[start:])
            if isinstance(value, dict): return value
        except json.JSONDecodeError:
            pass
        start = text.find("{", start + 1)
    return {"winner": "UNKNOWN", "reasoning": text[:500]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--model", default="openai-codex/gpt-5.4")
    parser.add_argument("--thinking", default="medium")
    args = parser.parse_args()
    manifest = json.loads(Path(args.manifest).read_text())
    expected = {case["id"]: case.get("expected_behavior", []) for case in manifest.get("cases", [])}
    results = []
    for line in Path(args.tasks).read_text().splitlines():
        task = json.loads(line)
        answer_a = Path(task["output_a_path"]).read_text(errors="replace")
        answer_b = Path(task["output_b_path"]).read_text(errors="replace")
        prompt = (
            "Blindly compare two candidate answers to the same testing-guidance task. "
            "Judge correctness, operational safety, completeness, and restraint against the criteria. "
            "Ignore style and length unless they affect actionability. Return ONLY JSON: "
            '{"winner":"A"|"B"|"TIE","reasoning":"one concise sentence"}.\n\n'
            f"TASK:\n{task['prompt']}\n\nCRITERIA:\n{json.dumps(expected.get(task['case_id'], []))}\n\n"
            f"ANSWER A:\n{answer_a}\n\nANSWER B:\n{answer_b}"
        )
        proc = subprocess.run(
            ["pi", "--model", args.model, "--thinking", args.thinking, "--no-tools", "--no-skills",
             "--no-context-files", "--no-session", "-p"],
            input=prompt, text=True, capture_output=True, timeout=300,
        )
        result = parse_json(proc.stdout or proc.stderr)
        result["comparison_task_id"] = task["comparison_task_id"]
        result["judge_requested_model"] = args.model
        result["returncode"] = proc.returncode
        results.append(result)
    Path(args.out).write_text("\n".join(json.dumps(result) for result in results) + "\n")
    print(f"wrote {len(results)} comparison results")
    return 0 if all(result.get("winner") in {"A", "B", "TIE"} for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
