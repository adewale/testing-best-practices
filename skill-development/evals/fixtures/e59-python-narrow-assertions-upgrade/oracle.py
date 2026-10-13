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

def deposit_comparisons(body: str) -> dict[str, list[tuple[ast.expr, ast.expr]]]:
    """Direct assertions after a literal deposit, on that same binding.

    Deliberately a bounded static shape check: it does not execute candidate
    Python or infer arbitrary control flow, helpers, aliases or parametrisation.
    Nested unused functions and assertions before the call are not evidence.
    """
    function = ast.parse(body).body[0]
    comparisons: dict[str, list[tuple[ast.expr, ast.expr]]] = {}
    for statement in function.body:
        if isinstance(statement, ast.Assign):
            for target in statement.targets:
                if isinstance(target, ast.Name):
                    comparisons.pop(target.id, None)
        if isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call):
            call = statement.value
            if (isinstance(call.func, ast.Name) and call.func.id == "apply_deposit"
                    and len(call.args) >= 3 and isinstance(call.args[0], ast.Name)
                    and isinstance(call.args[1], ast.Constant) and call.args[1].value == 50
                    and isinstance(call.args[2], ast.Constant) and call.args[2].value == "salary"):
                comparisons[call.args[0].id] = []
        pairs = []
        if isinstance(statement, ast.Assert):
            value = statement.test
            if isinstance(value, ast.Compare) and len(value.ops) == 1 and isinstance(value.ops[0], ast.Eq):
                pairs.append((value.left, value.comparators[0]))
        elif isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call):
            call = statement.value
            if isinstance(call.func, ast.Attribute) and call.func.attr in {"assertEqual", "assertDictEqual"} and len(call.args) >= 2:
                pairs.append((call.args[0], call.args[1]))
        for assertions in comparisons.values():
            assertions.extend(pairs)
    return comparisons


def records_expected_balance(body: str) -> bool:
    for account, comparisons in deposit_comparisons(body).items():
        for left, right in comparisons:
            for actual, literal in ((left, right), (right, left)):
                if (ast.unparse(actual) == f"{account}.balance"
                        and isinstance(literal, ast.Constant) and literal.value == 150):
                    return True
    return False


def records_expected_transaction(body: str) -> bool:
    """Check literal transaction equality, not merely the word transactions.

    This is static shape evidence, not execution of the proposed tests. Accept
    equality of the transaction list, or a single transaction with a length
    check and either dict equality or all three literal field expectations.
    """
    expected = {"kind": "deposit", "amount": 50, "memo": "salary"}
    for account, comparisons in deposit_comparisons(body).items():
        length = False
        row = False
        fields = set()
        for left, right in comparisons:
            for actual, literal in ((left, right), (right, left)):
                try:
                    value = ast.literal_eval(literal)
                except (ValueError, TypeError):
                    continue
                expression = ast.unparse(actual)
                if expression == f"{account}.transactions" and value == [expected]:
                    return True
                if expression == f"len({account}.transactions)" and value == 1:
                    length = True
                if expression == f"{account}.transactions[0]" and value == expected:
                    row = True
                for field, want in expected.items():
                    if expression == f"{account}.transactions[0][{field!r}]" and value == want:
                        fields.add(field)
        if length and (row or fields == set(expected)):
            return True
    return False


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
        records_expected_balance(body)
        for body, assertions in tests
    ):
        errors.append("no narrow assertion that the balance is 150 after the deposit")
    if not any(
        records_expected_transaction(body)
        for body, assertions in tests
    ):
        errors.append("no literal assertion of the single recorded deposit (kind, amount and memo)")

    for e in errors:
        print(e, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
