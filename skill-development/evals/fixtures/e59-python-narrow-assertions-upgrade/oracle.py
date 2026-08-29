#!/usr/bin/env python3
"""Oracle for E59: the repaired test must assert the deposit behavior
narrowly (balance, recorded transaction) instead of whole-object equality.

Failing shapes:
  - the change-detector treadmill: keeping the full asdict()/whole-object
    equality and just adding the new schema_version key to the literal;
  - dropping behavior coverage (no balance or no transaction assertion).

Judged over actual assert statements and expected-value assignments via the
AST, as in E55, so comments/docstrings quoting the old test do not count.
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


def judged_segments(src: str) -> list[str] | None:
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
            fn = node.func
            name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", "")
            if name in {"param", "assertEqual", "assertNotEqual", "assertDictEqual"}:
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
    segments: list[str] = []
    for f in files:
        segs = judged_segments(f.read_text(errors="ignore"))
        if segs is None:
            errors.append(f"{f.name}: not parseable as python")
        else:
            segments.extend(segs)
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
    if not BALANCE_OK.search(joined):
        errors.append("no narrow assertion that the balance is 150 after the deposit")
    if "transactions" not in joined:
        errors.append("no assertion on the recorded transaction")

    for e in errors:
        print(e, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
