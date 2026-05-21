#!/usr/bin/env python3
"""Approximate token usage for installable skill versions.

Uses a transparent approximation: tokens ~= characters / 4. This is not a
model tokenizer, so report chars/words alongside token estimates.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSIONS = {
    "first-github-6951b7d": ROOT / "github-skill-first-working" / "testing-best-practices",
    "github-origin-main-6e8cd8b": ROOT / "github-skill-origin-main" / "testing-best-practices",
    "local-working-tree": ROOT.parent / "testing-best-practices",
}


def metrics(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")
    chars = len(text)
    words = len(re.findall(r"\S+", text))
    approx = round(chars / 4)
    return {"chars": chars, "words": words, "approx_tokens_chars_div_4": approx}


def collect(root: Path) -> dict:
    files = [root / "SKILL.md", *sorted((root / "references").glob("*.md"))]
    skill = metrics(root / "SKILL.md")
    total_text = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in files if p.exists())
    total_path = root / ".__tmp_total__.md"
    total_path.write_text(total_text, encoding="utf-8")
    total = metrics(total_path)
    total_path.unlink()
    return {"skill_md": skill, "installable_total": total, "file_count": len([p for p in files if p.exists()])}


def main() -> int:
    out = {name: collect(path) for name, path in VERSIONS.items()}
    print(json.dumps(out, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
