#!/usr/bin/env python3
"""Reconstruct the frozen replay inputs without invoking models or scoring them."""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import subprocess
from pathlib import Path

STUDY = Path(__file__).resolve().parent
ROOT = STUDY.parents[1]
RESPONSE_FORMAT = (
    "Return ONLY a JSON object with these keys: decision (approve/revise/reject), "
    "changes (array of objects with target, action, details), retained_contracts "
    "(array of strings), validation (array of concrete commands or checks), "
    "cost_and_stop (string), rationale (string). Propose concrete changes you "
    "would actually ship, not just warnings. Stay within the supplied task. "
    "Do not execute the proposed work. Keep the JSON answer under 650 words."
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--judges", action="store_true", help="reconstruct the retained blind judge inputs")
    args = parser.parse_args()
    protocol = json.loads((STUDY / "protocol.json").read_text())
    cases = json.loads((STUDY / "cases.json").read_text())
    args.out.mkdir(parents=True, exist_ok=True)
    if args.judges:
        instructions = (STUDY / "grading-instructions.md").read_text()
        by_id = {case["id"]: case for case in cases}
        jobs = json.loads((STUDY / "judge-map.json").read_text())
        for job in jobs:
            case = by_id[job["case"]]
            candidates = [{
                "id": identifier,
                "answer": json.loads((STUDY / "outputs" / (identifier + ".json")).read_text()),
            } for identifier in job["candidate_ids"]]
            evidence = {
                "case": case["id"], "task": case["prompt"],
                "criteria": [{"criterion": i, "requirement": requirement}
                             for i, requirement in enumerate(case["criteria"], 1)],
                "candidates": candidates,
            }
            packet = instructions + "\n\n# Evidence\n\n" + json.dumps(evidence, indent=2) + "\n"
            (args.out / (job["id"] + ".md")).write_text(packet)
        print(f"Prepared {len(jobs)} judge packets; no model calls or grading performed.")
        return
    jobs = []
    for case in cases:
        for arm in protocol["arms"]:
            identifier = hashlib.sha256(
                f"replay-{protocol['date']}:{case['id']}:{arm}".encode()
            ).hexdigest()[:12]
            guidance = ""
            if arm != "none":
                revision = protocol["base_revision"] if arm == "base" else protocol["pr_revision"]
                paths = ["testing-best-practices/SKILL.md"] + [
                    "testing-best-practices/references/" + name for name in case["references"]
                ]
                if arm == "pr41":
                    paths.append("testing-best-practices/references/test-audit.md")
                parts = []
                for path in paths:
                    content = subprocess.check_output(
                        ["git", "show", revision + ":" + path], cwd=ROOT, text=True
                    )
                    parts.append(f"## Supplied guidance: {path}\n\n{content}")
                guidance = "\n\n".join(parts) + "\n\n"
            packet = (
                "Use only the task and context in this packet. Do not browse other files, "
                "use the network, run proposed checks, or contact other agents.\n\n"
                + guidance
                + "## Task\n\n" + case["prompt"]
                + "\n\n## Response format\n\n" + RESPONSE_FORMAT + "\n"
            )
            packet_path = args.out / (identifier + ".md")
            packet_path.write_text(packet)
            jobs.append({
                "id": identifier,
                "case": case["id"],
                "arm": arm,
                "packet": str(packet_path),
                "packet_sha256": hashlib.sha256(packet.encode()).hexdigest(),
            })
    random.Random(int(protocol["date"].replace("-", ""))).shuffle(jobs)
    (args.out / "generation-map.json").write_text(json.dumps(jobs, indent=2) + "\n")
    print(f"Prepared {len(jobs)} packets; no model calls or grading performed.")


if __name__ == "__main__":
    main()
