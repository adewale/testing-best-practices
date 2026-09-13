#!/usr/bin/env python3
"""Adapter: run a skill-development fixture oracle over shared-harness output.

The shared Skill Eval Harness saves candidate answers as
``runs/<case>/<variant>/output.md``. The Google-Testing-Blog-derived fixture
oracles under ``skill-development/evals/fixtures/`` judge candidate *files*
(``*.py`` via AST, or assessment ``*.md``). This adapter bridges the two:

1. Copies the output dir's files into a temp judged dir.
2. Extracts fenced code blocks from every ``*.md`` into real files
   (```python -> .py, ```go -> .go) so code-reading oracles can parse them.
3. Invokes the named fixture's ``oracle.py`` on the judged dir and forwards
   its exit code and output.

Usage: gtb_output_adapter.py OUTPUT_DIR FIXTURE_DIR_NAME
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "skill-development" / "evals" / "fixtures"

FENCE = re.compile(r"```(python|py|go)\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)
EXT = {"python": ".py", "py": ".py", "go": ".go"}


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: gtb_output_adapter.py OUTPUT_DIR FIXTURE_DIR_NAME", file=sys.stderr)
        return 2
    output_dir = Path(sys.argv[1])
    fixture = FIXTURES / sys.argv[2]
    oracle = fixture / "oracle.py"
    if not oracle.exists():
        print(f"unknown fixture oracle: {oracle}", file=sys.stderr)
        return 2
    if not output_dir.is_dir():
        print(f"missing output dir: {output_dir}", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory() as td:
        judged = Path(td)
        for src in output_dir.rglob("*"):
            if src.is_file():
                dst = judged / src.relative_to(output_dir)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(src, dst)
        for md in judged.rglob("*.md"):
            for i, match in enumerate(FENCE.finditer(md.read_text(errors="ignore"))):
                lang, body = match.group(1).lower(), match.group(2)
                out = judged / f"extracted_{md.stem}_{i}{EXT[lang]}"
                out.write_text(body)
        proc = subprocess.run(
            [sys.executable, str(oracle), str(judged)],
            cwd=fixture, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            timeout=280,
        )
        sys.stdout.write(proc.stdout)
        return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
