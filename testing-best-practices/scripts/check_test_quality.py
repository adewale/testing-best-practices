#!/usr/bin/env python3
"""Check test quality metrics for Python test files.

Usage:
    python check_test_quality.py <test_file_or_directory>
    python check_test_quality.py tests/
    python check_test_quality.py tests/test_parser.py

Reports:
    - Assertion density per test function (target: 3+)
    - Unconditional skips
    - Logging-not-asserting (print/log in conditionals)
    - "Not empty" weak assertions
    - Tests with zero assertions
    - Mock usage in integration test directories

Exit code: 0 if no P0 issues, 1 if P0 issues found.
"""

import ast
import os
import re
import sys
from pathlib import Path


def find_test_files(path: str) -> list[Path]:
    p = Path(path)
    if p.is_file():
        return [p] if p.suffix == ".py" else []
    return sorted(p.rglob("test_*.py")) + sorted(p.rglob("*_test.py"))


def count_assertions(node: ast.FunctionDef) -> int:
    count = 0
    for child in ast.walk(node):
        if isinstance(child, ast.Assert):
            count += 1
        elif isinstance(child, ast.Call):
            func = child.func
            name = ""
            if isinstance(func, ast.Attribute):
                name = func.attr
            elif isinstance(func, ast.Name):
                name = func.id
            if name.startswith("assert") or name.startswith("expect"):
                count += 1
            if name in ("assertEqual", "assertNotEqual", "assertTrue",
                        "assertFalse", "assertIn", "assertNotIn",
                        "assertRaises", "assertIsNone", "assertIsNotNone",
                        "assertAlmostEqual", "assertGreater",
                        "assertGreaterEqual", "assertLess", "assertLessEqual",
                        "assertRegex", "assertCountEqual", "assertIs"):
                count += 1
    return count


def find_weak_assertions(source: str) -> list[dict]:
    issues = []
    for i, line in enumerate(source.splitlines(), 1):
        stripped = line.strip()
        # "not None" / "is not None" as sole assertion
        if re.search(r"assert\s+\w+\s+is\s+not\s+None\s*$", stripped):
            issues.append({"line": i, "type": "weak-not-none", "text": stripped})
        # "!= {}" or "!= ''" as sole assertion
        if re.search(r"assert\s+\w+\s*!=\s*(\{\}|\"\"|\'\')s*$", stripped):
            issues.append({"line": i, "type": "weak-not-empty", "text": stripped})
        # truthiness assertion
        if re.search(r"^\s*assert\s+\w+\s*$", stripped):
            issues.append({"line": i, "type": "weak-truthy", "text": stripped})
    return issues


def find_logging_in_conditionals(source: str) -> list[dict]:
    issues = []
    lines = source.splitlines()
    in_if = False
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("if "):
            in_if = True
        elif in_if and re.search(r"\bprint\s*\(", stripped):
            issues.append({"line": i, "type": "print-not-assert", "text": stripped})
            in_if = False
        elif in_if and not stripped.startswith((" ", "\t", "#")):
            in_if = False
    return issues


def find_unconditional_skips(source: str) -> list[dict]:
    issues = []
    for i, line in enumerate(source.splitlines(), 1):
        stripped = line.strip()
        if re.search(r"@pytest\.mark\.skip\b", stripped) and "skipif" not in stripped:
            issues.append({"line": i, "type": "unconditional-skip", "text": stripped})
        if re.search(r"@unittest\.skip\b", stripped):
            issues.append({"line": i, "type": "unconditional-skip", "text": stripped})
    return issues


def find_mock_in_integration(filepath: Path, source: str) -> list[dict]:
    issues = []
    if "integration" in str(filepath):
        for i, line in enumerate(source.splitlines(), 1):
            if re.search(r"@(mock\.)?patch|@mock\.patch|Mock\(\)|MagicMock\(\)", line):
                issues.append({"line": i, "type": "mock-in-integration", "text": line.strip()})
    return issues


def analyze_file(filepath: Path) -> dict:
    source = filepath.read_text()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {"file": str(filepath), "error": "SyntaxError", "functions": [], "issues": []}

    functions = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("test_"):
                assertions = count_assertions(node)
                functions.append({
                    "name": node.name,
                    "line": node.lineno,
                    "assertions": assertions,
                })

    issues = []
    issues.extend(find_weak_assertions(source))
    issues.extend(find_logging_in_conditionals(source))
    issues.extend(find_unconditional_skips(source))
    issues.extend(find_mock_in_integration(filepath, source))

    total_assertions = sum(f["assertions"] for f in functions)
    avg_density = total_assertions / len(functions) if functions else 0
    zero_assertion = [f for f in functions if f["assertions"] == 0]

    return {
        "file": str(filepath),
        "test_count": len(functions),
        "total_assertions": total_assertions,
        "avg_density": round(avg_density, 2),
        "zero_assertion_tests": zero_assertion,
        "issues": issues,
        "functions": functions,
    }


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <test_file_or_directory>")
        sys.exit(2)

    target = sys.argv[1]
    files = find_test_files(target)
    if not files:
        print(f"No test files found in {target}")
        sys.exit(2)

    has_p0 = False
    results = []

    for f in files:
        result = analyze_file(f)
        results.append(result)

    # Print report
    print("=" * 60)
    print("TEST QUALITY REPORT")
    print("=" * 60)

    for r in results:
        if "error" in r:
            print(f"\n{r['file']}: {r['error']}")
            continue

        density_marker = "OK" if r["avg_density"] >= 3 else "LOW"
        print(f"\n{r['file']}")
        print(f"  Tests: {r['test_count']}  Assertions: {r['total_assertions']}  "
              f"Density: {r['avg_density']} [{density_marker}]")

        if r["zero_assertion_tests"]:
            print(f"  Zero-assertion tests:")
            for f in r["zero_assertion_tests"]:
                print(f"    line {f['line']}: {f['name']}")

        for issue in r["issues"]:
            severity = "P0" if issue["type"] == "print-not-assert" else "P1"
            if severity == "P0":
                has_p0 = True
            print(f"  [{severity}] line {issue['line']}: {issue['type']}")
            print(f"         {issue['text']}")

    # Summary
    total_tests = sum(r.get("test_count", 0) for r in results)
    total_assertions = sum(r.get("total_assertions", 0) for r in results)
    overall_density = total_assertions / total_tests if total_tests else 0
    total_issues = sum(len(r.get("issues", [])) for r in results)

    print(f"\n{'=' * 60}")
    print(f"SUMMARY")
    print(f"  Files: {len(results)}")
    print(f"  Tests: {total_tests}")
    print(f"  Assertions: {total_assertions}")
    print(f"  Overall density: {overall_density:.2f} (target: 3.0+)")
    print(f"  Issues found: {total_issues}")
    print(f"{'=' * 60}")

    sys.exit(1 if has_p0 else 0)


if __name__ == "__main__":
    main()
