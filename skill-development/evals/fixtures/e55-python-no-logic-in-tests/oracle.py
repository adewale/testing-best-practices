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
its module docstring).
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


def judged_segments(src: str) -> list[str] | None:
    """Source segments of assert statements and expected*/want* assignments."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    segments: list[str] = []
    for node in ast.walk(tree):
        seg = None
        if isinstance(node, ast.Assert):
            seg = ast.get_source_segment(src, node)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names = [t.id for t in targets if isinstance(t, ast.Name)]
            if any(n.lower().startswith(("expected", "want")) for n in names):
                seg = ast.get_source_segment(src, node)
        elif isinstance(node, ast.Call):
            # pytest.param(...) rows and assertEqual-style calls carry
            # expected values too.
            fn = node.func
            name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", "")
            if name in {"param", "assertEqual", "assertNotEqual"}:
                seg = ast.get_source_segment(src, node)
        if seg:
            segments.append(seg)
    return segments


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    files = sorted(root.rglob("*.py"))
    if not files:
        print("no python candidate files found", file=sys.stderr)
        return 1

    errors: list[str] = []
    all_segments: list[str] = []
    for f in files:
        segs = judged_segments(f.read_text(errors="ignore"))
        if segs is None:
            errors.append(f"{f.name}: not parseable as python")
        else:
            all_segments.extend(segs)
    joined = "\n".join(all_segments)

    if not all_segments and not errors:
        errors.append("no assert statements found in candidate files")

    if not LITERAL_OK.search(joined):
        errors.append(
            "no assertion against a literal single-slash URL "
            "(expected e.g. \"https://example.com/users/bob\")"
        )
    if LITERAL_BUGGY.search(joined):
        errors.append("literal expectation enshrines the double-slash bug")

    computed = [s.splitlines()[0].strip() for s in all_segments if COMPUTED.search(s)]
    if computed:
        errors.append(f"expected values still computed from BASE_URL/base: {computed[:2]}")

    for e in errors:
        print(e, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
