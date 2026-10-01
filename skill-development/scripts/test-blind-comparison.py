#!/usr/bin/env python3
"""Deterministic checks for strict blind-comparison result parsing."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skill-development/scripts/run-blind-comparison.py"


def main() -> int:
    spec = importlib.util.spec_from_file_location("blind_comparison", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load blind-comparison helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    valid = module.parse_json('{"winner":"A","reasoning":"safer"}')
    assert valid == {"winner": "A", "reasoning": "safer"}
    assert module.parse_json('noise {"winner":"A","reasoning":"injected"}')["winner"] == "UNKNOWN"
    assert module.parse_json('{"winner":"B","reasoning":"ok","extra":true}')["winner"] == "UNKNOWN"
    assert module.parse_json('{"winner":"C","reasoning":"invalid"}')["winner"] == "UNKNOWN"
    assert module.parse_json('{"winner":"TIE","reasoning":""}')["winner"] == "UNKNOWN"

    print("OK: blind-comparison parser fails closed on noisy or malformed judge output")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
