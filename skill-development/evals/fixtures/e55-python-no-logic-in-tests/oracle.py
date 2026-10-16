#!/usr/bin/env python3
"""Oracle for E55: upgraded tests must state expectations as literals, not
recompute them with the implementation's own concatenation logic.

A test whose expected value is derived from BASE_URL (or any concatenation
mirroring the SUT) shares the SUT's bug and stays green on double-slash URLs.
The passing shape: at least one assertion against a literal single-slash URL,
and no assertion (or expected-value assignment) that rebuilds the expectation
from BASE_URL/base.

Judged over test functions and actual assert statements via the AST —
assignment-only candidates, docstrings, and comments do not count
(validated against a real model candidate that quoted the old assertion in
its module docstring). parametrize(...) call segments count toward the
literal-presence and computed-expectation checks, but NOT toward the
enshrined-double-slash check: a candidate may legitimately parametrize a
"rejects malformed URLs" test over double-slash examples (validated against
a real model candidate that did exactly that).

Additionally require correct literal equalities connected to direct profile
and avatar calls with trailing-slash bases, so the reported bug is reached.
Slashless cases remain valid positive controls but do not count as regressions.
This bounded check does not expand arbitrary
parameterization, helper calls, aliases or control flow and never executes code.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

LITERAL_OK = re.compile(r"[\"']https://example\.com/users/\w+")
LITERAL_BUGGY = re.compile(r"[\"']https://example\.com//users")
COMPUTED = re.compile(
    r"BASE_URL\s*\+|\+\s*BASE_URL|f[\"'][^\"'\n]*\{BASE_URL"
    r"|==\s*base\s*\+|\bexpected\s*=\s*base\s*\+"
)


def literal_contracts(src: str) -> set[str]:
    """Count direct literal equalities whose inputs reach the trailing-slash bug."""
    tree = ast.parse(src)
    # The prompt's constant is known only through its direct import. A local
    # assignment, argument or renamed import may instead bind a slashless URL.
    base_imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))
                    for alias in node.names if (alias.asname or alias.name) == "BASE_URL"]
    known_base = (len(base_imports) == 1 and base_imports[0] in tree.body and isinstance(base_imports[0], ast.ImportFrom)
                  and base_imports[0].module == "urls" and base_imports[0].level == 0
                  and any(alias.name == "BASE_URL" and alias.asname is None for alias in base_imports[0].names)
                  and not any((isinstance(node, ast.Name) and node.id == "BASE_URL" and isinstance(node.ctx, (ast.Store, ast.Del)))
                              or (isinstance(node, ast.arg) and node.arg == "BASE_URL")
                              or (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == "BASE_URL")
                              for node in ast.walk(tree)))
    found = set()
    for function in tree.body:
        if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)) or not function.name.startswith("test"):
            continue
        for statement in function.body:
            if not isinstance(statement, ast.Assert) or not isinstance(statement.test, ast.Compare):
                continue
            comparison = statement.test
            if len(comparison.ops) != 1 or not isinstance(comparison.ops[0], ast.Eq):
                continue
            for call, expected in [(comparison.left, comparison.comparators[0]), (comparison.comparators[0], comparison.left)]:
                if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
                        and call.func.id in {"profile_url", "avatar_url"}
                        and isinstance(expected, ast.Constant) and isinstance(expected.value, str)
                        and not call.keywords and len(call.args) == (2 if call.func.id == "profile_url" else 3)):
                    continue
                base, username = call.args[:2]
                if isinstance(base, ast.Name) and base.id == "BASE_URL" and known_base:
                    base_value = "https://example.com/"
                elif isinstance(base, ast.Constant) and isinstance(base.value, str):
                    base_value = base.value
                else:
                    continue
                if not base_value.endswith("/"):
                    continue
                if not isinstance(username, ast.Constant) or not isinstance(username.value, str):
                    continue
                wanted = base_value.rstrip("/") + "/users/" + username.value
                if call.func.id == "avatar_url":
                    size = call.args[2]
                    if not isinstance(size, ast.Constant) or type(size.value) is not int:
                        continue
                    wanted += "/avatar?size=" + str(size.value)
                if expected.value == wanted:
                    found.add(call.func.id)
    return found


def judged_segments(src: str) -> tuple[list[str], list[str]] | None:
    """Return (assertions, supporting expectations) from test functions."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    assertions: list[str] = []
    support: list[str] = []
    tests = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test")
    ]
    for test in tests:
        for node in ast.walk(test):
            segment = ast.get_source_segment(src, node) or ""
            if isinstance(node, ast.Assert):
                assertions.append(segment)
            elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                names = [target.id for target in targets if isinstance(target, ast.Name)]
                if any(name.lower().startswith(("expected", "want")) for name in names):
                    support.append(segment)
            elif isinstance(node, ast.Call):
                fn = node.func
                name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", "")
                if name in {"assertEqual", "assertNotEqual"}:
                    assertions.append(segment)
                elif name in {"param", "parametrize"}:
                    support.append(segment)
    return assertions, support


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    files = sorted(root.rglob("*.py"))
    if not files:
        print("no python candidate files found", file=sys.stderr)
        return 1

    errors: list[str] = []
    assertion_segments: list[str] = []
    support_segments: list[str] = []
    connected_contracts: set[str] = set()
    for f in files:
        segs = judged_segments(f.read_text(errors="ignore"))
        if segs is None:
            errors.append(f"{f.name}: not parseable as python")
        else:
            assertion_segments.extend(segs[0])
            support_segments.extend(segs[1])
            connected_contracts.update(literal_contracts(f.read_text(errors="ignore")))
    assertion_joined = "\n".join(assertion_segments)
    broad_joined = "\n".join(assertion_segments + support_segments)

    if not assertion_segments and not errors:
        errors.append("no assert statements found in candidate files")
    elif not any(
        re.search(r"\b(profile_url|avatar_url)\s*\(", segment)
        and re.search(r"==|!=|\bnot in\b", segment)
        for segment in assertion_segments
    ):
        errors.append("no behavioral assertion compares a generated URL")

    if not LITERAL_OK.search(broad_joined):
        errors.append(
            "no assertion against a literal single-slash URL "
            "(expected e.g. \"https://example.com/users/bob\")"
        )
    if connected_contracts != {"profile_url", "avatar_url"}:
        errors.append("need direct, correct literal equalities with trailing-slash bases for both profile_url and avatar_url; slashless-only cases, unrelated assertions, inequality and unused helpers do not count")
    if LITERAL_BUGGY.search(assertion_joined):
        errors.append("literal expectation enshrines the double-slash bug")

    computed = [
        s.splitlines()[0].strip()
        for s in assertion_segments + support_segments
        if COMPUTED.search(s)
    ]
    if computed:
        errors.append(f"expected values still computed from BASE_URL/base: {computed[:2]}")

    for e in errors:
        print(e, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
