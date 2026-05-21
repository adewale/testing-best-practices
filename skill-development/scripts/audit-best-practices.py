#!/usr/bin/env python3
"""Audit repo/eval best practices for the testing-best-practices skill.

This is intentionally conservative and stdlib-only. It checks hygiene and eval
validity practices that are easy to regress.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent


def git_files() -> list[str]:
    try:
        out = subprocess.check_output(["git", "ls-files"], cwd=REPO, text=True)
    except Exception:
        return []
    return [line for line in out.splitlines() if line]


def check(name: str, ok: bool, detail: str, weight: int, rows: list[dict]) -> None:
    rows.append({"name": name, "ok": ok, "detail": detail, "weight": weight, "score": weight if ok else 0})


def main() -> int:
    rows: list[dict] = []
    files = git_files()

    installable = [p for p in files if p.startswith("testing-best-practices/")]
    bad_installable = [p for p in installable if not (p == "testing-best-practices/SKILL.md" or (p.startswith("testing-best-practices/references/") and p.endswith(".md")))]
    check("installable skill boundary", not bad_installable, f"unexpected installable files: {bad_installable[:5]}", 15, rows)

    generated = [p for p in files if "__pycache__" in p or p.endswith(".pyc") or p.startswith("skill-development/eval-runs/")]
    check("no tracked generated run/cache artifacts", not generated, f"tracked generated artifacts: {len(generated)}", 20, rows)

    evals = json.loads((ROOT / "evals" / "evals.json").read_text())["evals"]
    missing_validity = [e["id"] for e in evals if not all(k in e.get("validity", {}) for k in ["claim", "warrant", "backing", "rebuttals"])]
    check("claim-based validity metadata", not missing_validity, f"missing validity: {missing_validity[:5]}", 15, rows)

    missing_health = [e["id"] for e in evals if not all(k in e.get("eval_health", {}) for k in ["difficulty", "saturation_status", "known_discriminates_versions", "last_reviewed"])]
    check("difficulty/saturation/discrimination metadata", not missing_health, f"missing eval_health: {missing_health[:5]}", 15, rows)

    hidden_hard = [e for e in evals if e.get("hidden") and e.get("eval_health", {}).get("difficulty") in {"hard", "adversarial"}]
    check("hidden hard/adversarial probes", len(hidden_hard) >= 5, f"hidden hard/adversarial probes: {len(hidden_hard)}", 10, rows)

    mini = sorted((ROOT / "evals" / "mini-repos").glob("*/manifest.json"))
    langs = {json.loads(p.read_text()).get("language") for p in mini}
    check("mutation-backed mini-repos", len(mini) >= 3 and {"javascript", "python", "go"}.issubset(langs), f"mini-repos: {len(mini)}, languages: {sorted(langs)}", 10, rows)

    schema = (ROOT / "evals" / "schema.json").read_text()
    schema_ok = all(token in schema for token in ["validity", "eval_health", "hidden", "saturation_status"])
    check("schema covers eval metadata", schema_ok, "schema should validate hidden/validity/eval_health fields", 10, rows)

    ignore = (REPO / ".gitignore").read_text() if (REPO / ".gitignore").exists() else ""
    ignore_ok = all(token in ignore for token in ["__pycache__/", "*.pyc", "skill-development/eval-runs/"])
    check("generated-artifact ignore rules", ignore_ok, ".gitignore covers caches and eval-runs", 5, rows)

    total = sum(r["weight"] for r in rows)
    score = sum(r["score"] for r in rows)
    result = {"score": score, "total": total, "percent": round(score / total * 100, 1), "checks": rows}
    print(json.dumps(result, indent=2))
    if score != total:
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
