#!/usr/bin/env python3
"""Data-only decision grading shared by local and benchmark entrypoints."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "evals" / "oracles"))
from decision_vectors import main

if __name__ == "__main__":
    raise SystemExit(main("e66-combinatorial-cost-aware-portfolio"))
