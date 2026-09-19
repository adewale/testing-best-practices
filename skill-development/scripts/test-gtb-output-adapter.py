#!/usr/bin/env python3
"""Regression check for fenced-code extraction used by shared GTB evals."""
from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path

ADAPTER = Path(__file__).resolve().parents[2] / "evals" / "oracles" / "gtb_output_adapter.py"
SPEC = importlib.util.spec_from_file_location("gtb_output_adapter", ADAPTER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - import contract
    raise RuntimeError(f"cannot load {ADAPTER}")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "output.md").write_text("```python\ndef test_contract():\n    assert True\n```\n")
        extracted = MODULE.extract_fenced_files(root)
        assert [path.name for path in extracted] == ["test_extracted_output_0.py"]
        assert "def test_contract" in extracted[0].read_text()
    print("OK: shared GTB adapter emits test-discoverable Python filenames")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
