#!/usr/bin/env python3
"""Adapt development fixture oracles to Skill Eval Harness output directories.

Prose fixtures receive only output.md in a fresh directory. E67 model-supplied
Python is never imported or executed here: named fences are materialized in a
temporary directory and checked with AST-only shape analysis. The development
fixture's dynamic execution remains a trusted local self-test, not a shared
harness assertion for untrusted candidates.
"""
from __future__ import annotations

import ast
import importlib.util
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "skill-development" / "evals" / "fixtures"


def extract_e67(output: Path, candidate: Path) -> list[str]:
    text = output.read_text(errors="replace")
    blocks = re.findall(r"```(?:python|py)?\s*\n(.*?)```", text, re.IGNORECASE | re.DOTALL)
    portfolio = next((block for block in blocks if "REGISTRY" in block and "def one_way_cases" in block), None)
    tests = next((block for block in blocks if "unittest" in block and "contract_passes" in block), None)
    errors: list[str] = []
    if portfolio is None:
        errors.append("missing a Python code fence containing REGISTRY and one_way_cases")
    else:
        (candidate / "portfolio.py").write_text(portfolio)
    if tests is None:
        errors.append("missing a Python code fence containing the unittest contract tests")
    else:
        (candidate / "test_portfolio.py").write_text(tests)
    return errors


def e67_static_check(oracle: Path, candidate: Path) -> list[str]:
    errors: list[str] = []
    portfolio = candidate / "portfolio.py"
    tests = candidate / "test_portfolio.py"
    try:
        tree = ast.parse(portfolio.read_text())
    except (OSError, SyntaxError) as exc:
        return [f"cannot parse portfolio.py: {exc}"]
    top_level_names = {
        node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assigned = {
        target.id
        for node in tree.body if isinstance(node, ast.Assign)
        for target in node.targets if isinstance(target, ast.Name)
    }
    assigned.update(
        node.target.id for node in tree.body
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
    )
    if "REGISTRY" not in assigned:
        errors.append("portfolio.py has no top-level REGISTRY assignment")
    for required in ("one_way_cases", "contract_passes"):
        if required not in top_level_names:
            errors.append(f"portfolio.py has no top-level {required} function")

    spec = importlib.util.spec_from_file_location("e67_shape_oracle", oracle)
    if spec is None or spec.loader is None:
        return errors + ["cannot load trusted E67 AST checker"]
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    errors.extend(module.test_shape([tests]))
    return errors


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: development_fixture_oracle.py FIXTURE_NAME OUTPUT_DIR", file=sys.stderr)
        return 2
    fixture_name, output_dir_arg = sys.argv[1:]
    fixture = FIXTURES / fixture_name
    oracle = fixture / "oracle.py"
    output = Path(output_dir_arg) / "output.md"
    if not oracle.exists() or not output.exists():
        print(f"missing fixture oracle or output: {oracle}, {output}", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory(prefix="skill-eval-candidate-") as tmp:
        candidate = Path(tmp)
        if fixture_name.startswith("e67-"):
            errors = extract_e67(output, candidate)
            if not errors:
                errors.extend(e67_static_check(oracle, candidate))
            for error in errors:
                print(error, file=sys.stderr)
            return 1 if errors else 0

        (candidate / "output.md").write_text(output.read_text(errors="replace"))
        return subprocess.run([sys.executable, str(oracle), str(candidate)]).returncode


if __name__ == "__main__":
    raise SystemExit(main())
