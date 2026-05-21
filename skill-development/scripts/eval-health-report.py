#!/usr/bin/env python3
"""Report eval saturation/discrimination health."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    data = json.loads((ROOT / "evals" / "evals.json").read_text())
    evals = data["evals"]
    saturation = Counter(e.get("eval_health", {}).get("saturation_status", "missing") for e in evals)
    difficulty = Counter(e.get("eval_health", {}).get("difficulty", "missing") for e in evals)
    hidden = [e for e in evals if e.get("hidden")]
    saturated = [e["id"] for e in evals if e.get("eval_health", {}).get("saturation_status") == "saturated_public"]
    discriminating = [e["id"] for e in evals if e.get("eval_health", {}).get("known_discriminates_versions")]
    print(f"evals: {len(evals)}")
    print(f"hidden probes: {len(hidden)}")
    print("saturation:")
    for key, value in sorted(saturation.items()): print(f"  {key}: {value}")
    print("difficulty:")
    for key, value in sorted(difficulty.items()): print(f"  {key}: {value}")
    print(f"saturated_public: {len(saturated)}")
    for eid in saturated: print(f"  - {eid}")
    print(f"known discriminating evals: {len(discriminating)}")
    for eid in discriminating: print(f"  - {eid}")
    if len(hidden) < 5:
        print("ERROR: expected at least 5 hidden probes", file=sys.stderr)
        return 1
    if len(discriminating) < 5:
        print("ERROR: expected at least 5 known/proposed discriminating evals", file=sys.stderr)
        return 1
    print("OK: eval health report generated")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
