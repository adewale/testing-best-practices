#!/usr/bin/env python3
"""Oracle for E59: the repaired test must assert the deposit behavior
narrowly (balance, recorded transaction) instead of whole-object equality.

Failing shapes:
  - the change-detector treadmill: keeping the full asdict()/whole-object
    equality and just adding the new schema_version key to the literal;
  - dropping behavior coverage (no balance or no transaction assertion).

Judged over actual assertions inside test functions via the AST, as in E55,
so assignment-only candidates, comments, and docstrings do not count.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

BALANCE_OK = re.compile(
    r"(account\.balance|\[[\"']balance[\"']\]|\.balance)\s*==\s*150"
    r"|assertEqual\(\s*(account\.balance|[^,]*\[[\"']balance[\"']\])\s*,\s*150"
    r"|assertEqual\(\s*150\s*,\s*(account\.balance|[^,]*\[[\"']balance[\"']\])"
)


def judged_tests(src: str) -> list[tuple[str, list[str]]] | None:
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    tests: list[tuple[str, list[str]]] = []
    for test in ast.walk(tree):
        if not isinstance(test, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not test.name.startswith("test"):
            continue
        assertions: list[str] = []
        for node in ast.walk(test):
            segment = None
            if isinstance(node, ast.Assert):
                segment = ast.get_source_segment(src, node)
            elif isinstance(node, ast.Call):
                fn = node.func
                name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", "")
                if name in {"assertEqual", "assertNotEqual", "assertDictEqual"}:
                    segment = ast.get_source_segment(src, node)
            if segment:
                assertions.append(segment)
        tests.append((ast.get_source_segment(src, test) or "", assertions))
    return tests


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    files = sorted(root.rglob("*.py"))
    if not files:
        print("no python candidate files found", file=sys.stderr)
        return 1

    errors: list[str] = []
    tests: list[tuple[str, list[str]]] = []
    for f in files:
        judged = judged_tests(f.read_text(errors="ignore"))
        if judged is None:
            errors.append(f"{f.name}: not parseable as python")
        else:
            tests.extend(judged)
    segments = [segment for _, assertions in tests for segment in assertions]
    joined = "\n".join(segments)

    if not segments and not errors:
        errors.append("no assert statements found in candidate files")

    if re.search(r"\basdict\s*\(", joined):
        errors.append(
            "still asserts whole-object equality via asdict() — the test keeps "
            "implicitly testing every unrelated field"
        )
    if "schema_version" in joined:
        errors.append(
            "expectation enumerates the unrelated schema_version field "
            "(the change-detector treadmill: updating the literal per field addition)"
        )
    if not any(
        "apply_deposit" in body and BALANCE_OK.search("\n".join(assertions))
        for body, assertions in tests
    ):
        errors.append("no narrow assertion that the balance is 150 after the deposit")
    if not any(
        "apply_deposit" in body
        and any("transactions" in assertion for assertion in assertions)
        for body, assertions in tests
    ):
        errors.append("no assertion on the recorded transaction")

    for e in errors:
        print(e, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
