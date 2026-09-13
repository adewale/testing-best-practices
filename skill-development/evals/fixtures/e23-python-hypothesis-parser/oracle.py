#!/usr/bin/env python3
"""Structural oracle for the E23 Hypothesis parser property.

This intentionally checks the Python syntax tree rather than source keywords:
the property must call the parser and assert both successful and structured
error outcomes. Executing the project test suite remains the agent's reported
validation responsibility because this fixture does not contain the project.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

FUNCTION_NODES = (ast.FunctionDef, ast.AsyncFunctionDef)
CONFIG_FIELDS = {"name", "settings", "value"}
ERROR_FIELDS = {"message", "kind", "span"}


def final_name(node: ast.AST | None) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def parse_candidate(root: Path) -> tuple[list[ast.Module], list[str]]:
    trees = []
    errors = []
    files = sorted(root.rglob("*.py"))
    if not files:
        return [], ["no Python candidate found"]
    for path in files:
        try:
            trees.append(ast.parse(path.read_text(errors="ignore"), filename=str(path)))
        except SyntaxError as exc:
            errors.append(f"candidate does not parse: {path.name}:{exc.lineno}")
    return trees, errors


def imports_hypothesis(trees: list[ast.Module]) -> bool:
    for tree in trees:
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "hypothesis":
                return True
            if isinstance(node, ast.Import) and any(alias.name == "hypothesis" for alias in node.names):
                return True
    return False


def is_given_property(node: ast.AST) -> bool:
    if not isinstance(node, FUNCTION_NODES):
        return False
    for decorator in node.decorator_list:
        target = decorator.func if isinstance(decorator, ast.Call) else decorator
        if final_name(target) == "given":
            return True
    return False


def checked_result_types(properties: list[ast.AST]) -> set[str]:
    result = set()
    for prop in properties:
        for node in ast.walk(prop):
            if not isinstance(node, ast.Call) or final_name(node.func) != "isinstance" or len(node.args) < 2:
                continue
            type_arg = node.args[1]
            if isinstance(type_arg, ast.Tuple):
                result.update(final_name(item) for item in type_arg.elts)
            else:
                result.add(final_name(type_arg))
    return result


def swallowed_broad_exception(properties: list[ast.AST]) -> bool:
    for prop in properties:
        for node in ast.walk(prop):
            if not isinstance(node, ast.ExceptHandler):
                continue
            if node.type is not None and final_name(node.type) not in {"Exception", "BaseException"}:
                continue
            if any(isinstance(child, (ast.Pass, ast.Return)) for statement in node.body for child in ast.walk(statement)):
                return True
    return False


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    trees, errors = parse_candidate(root)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    if not imports_hypothesis(trees):
        errors.append("missing Hypothesis import")
    properties = [node for tree in trees for node in ast.walk(tree) if is_given_property(node)]
    if not properties:
        errors.append("missing Hypothesis @given property")

    parser_calls = [
        node
        for prop in properties
        for node in ast.walk(prop)
        if isinstance(node, ast.Call) and final_name(node.func).lower().startswith("parse")
    ]
    if not parser_calls:
        errors.append("Hypothesis property does not call the parser")

    checked_types = checked_result_types(properties)
    if "Config" not in checked_types:
        errors.append("property does not distinguish and check Config results")
    if "ParseError" not in checked_types:
        errors.append("property does not distinguish and check ParseError results")

    asserted_fields = {
        node.attr
        for prop in properties
        for assertion in ast.walk(prop)
        if isinstance(assertion, ast.Assert)
        for node in ast.walk(assertion.test)
        if isinstance(node, ast.Attribute)
    }
    if not asserted_fields.intersection(CONFIG_FIELDS):
        errors.append("missing asserted Config field invariant")
    if not asserted_fields.intersection(ERROR_FIELDS):
        errors.append("missing asserted ParseError field invariant")
    if swallowed_broad_exception(properties):
        errors.append("property swallows a broad exception instead of failing")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
