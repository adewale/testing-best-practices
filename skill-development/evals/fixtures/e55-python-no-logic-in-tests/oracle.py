#!/usr/bin/env python3
"""Oracle for E55: upgraded tests must state expectations as literals, not
recompute them with the implementation's own concatenation logic.

A test whose expected value is derived from BASE_URL (or any concatenation
mirroring the SUT) shares the SUT's bug and stays green on double-slash URLs.
The passing shape: at least one assertion against a literal single-slash URL,
and no assertion (or expected-value assignment) that rebuilds the expectation
from BASE_URL/base.

Judged over actual assert statements and expected-value assignments via the
AST — docstrings and comments quoting the old bad test do not count
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
    """(strict, parametrize) source segments.

    strict: assert statements, expected*/want* assignments, and
    param/assertEqual calls. parametrize: whole parametrize(...) calls,
    whose plain tuples carry expected literals."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    strict: list[str] = []
    params: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            strict.append(ast.get_source_segment(src, node) or "")
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names = [t.id for t in targets if isinstance(t, ast.Name)]
            if any(n.lower().startswith(("expected", "want")) for n in names):
                strict.append(ast.get_source_segment(src, node) or "")
        elif isinstance(node, ast.Call):
            fn = node.func
            name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", "")
            if name in {"param", "assertEqual", "assertNotEqual"}:
                strict.append(ast.get_source_segment(src, node) or "")
            elif name == "parametrize":
                params.append(ast.get_source_segment(src, node) or "")
    return strict, params


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    files = sorted(root.rglob("*.py"))
    if not files:
        print("no python candidate files found", file=sys.stderr)
        return 1

    errors: list[str] = []
    strict_segments: list[str] = []
    param_segments: list[str] = []
    for f in files:
        segs = judged_segments(f.read_text(errors="ignore"))
        if segs is None:
            errors.append(f"{f.name}: not parseable as python")
        else:
            strict_segments.extend(segs[0])
            param_segments.extend(segs[1])
    strict_joined = "\n".join(strict_segments)
    broad_joined = "\n".join(strict_segments + param_segments)

    if not strict_segments and not errors:
        errors.append("no assert statements found in candidate files")

    if not LITERAL_OK.search(broad_joined):
        errors.append(
            "no assertion against a literal single-slash URL "
            "(expected e.g. \"https://example.com/users/bob\")"
        )
    if LITERAL_BUGGY.search(strict_joined):
        errors.append("literal expectation enshrines the double-slash bug")

    computed = [
        s.splitlines()[0].strip()
        for s in strict_segments + param_segments
        if COMPUTED.search(s)
    ]
    if computed:
        errors.append(f"expected values still computed from BASE_URL/base: {computed[:2]}")

    for e in errors:
        print(e, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
