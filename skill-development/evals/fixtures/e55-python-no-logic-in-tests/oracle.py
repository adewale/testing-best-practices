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
    for f in files:
        segs = judged_segments(f.read_text(errors="ignore"))
        if segs is None:
            errors.append(f"{f.name}: not parseable as python")
        else:
            assertion_segments.extend(segs[0])
            support_segments.extend(segs[1])
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
