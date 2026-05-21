#!/usr/bin/env python3
"""Static audit for testing-best-practices skill docs.

This intentionally fails on the current baseline until Phase 1/2 fixes land.
It is a regression gate for known contradictions and unsafe wording from the
skill audit, not a general Markdown linter.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DEV_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = DEV_ROOT.parent
DEFAULT_SKILL_ROOT = REPO_ROOT / "testing-best-practices"
SKILL_ROOT = DEFAULT_SKILL_ROOT

P0_PATTERNS = [
    ("references/typescript.md", r"expect\(result\)\.toBeDefined\(\)", "sole toBeDefined() appears in TypeScript PBT example"),
    ("references/correctness-by-construction.md", r"In all six cases", "six/seven contradiction in correctness-by-construction"),
    ("references/vcr-cassettes.md", r"## TypeScript \(msw\)", "hand-written MSW mock section is labeled as VCR cassette guidance"),
    ("references/antipatterns.md", r"An integration test must have at least one real\s+external dependency", "integration tests incorrectly require an external dependency"),
    ("SKILL.md", r"Every test should verify what SHOULD be present", "positive+negative assertion rule is universal instead of scoped"),
    ("SKILL.md", r"delete the downstream checks \*\*and their tests\*\*", "downstream check deletion wording needs explicit safety preconditions"),
    ("references/correctness-by-construction.md", r"Email\{\} outside the package compiles", "Go unexported-field example should use zero value, not external Email{} literal"),
]

P1_PATTERNS = [
    ("SKILL.md", r"Always follow the Red-Green-Refactor cycle", "TDD wording should be a default with feasibility/scope exceptions"),
    ("SKILL.md", r"Aim for 3\+ meaningful assertions per test", "assertion-count heuristic needs calibration"),
    ("references/test-types.md", r"3\+ assertions per test, happy \+ sad path, no network/filesystem", "unit rules need temp-dir/in-memory and assertion-count calibration"),
    ("references/go.md", r"Every test should use this", "Go table-driven guidance is over-universal"),
    ("references/test-types.md", r"See the matching reference file", "generic cross-link should point to concrete local reference"),
]

LOCAL_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def read_rel(rel: str) -> str:
    path = SKILL_ROOT / rel
    return path.read_text(encoding="utf-8") if path.exists() else ""


def line_for(text: str, match_start: int) -> int:
    return text.count("\n", 0, match_start) + 1


def check_patterns(patterns: list[tuple[str, str, str]], severity: str) -> list[str]:
    findings: list[str] = []
    for rel, pattern, message in patterns:
        path = SKILL_ROOT / rel
        if not path.exists():
            findings.append(f"{severity} {rel}: missing file for check: {message}")
            continue
        text = read_rel(rel)
        m = re.search(pattern, text, flags=re.S)
        if m:
            findings.append(f"{severity} {rel}:{line_for(text, m.start())}: {message}")
    return findings


def check_links() -> list[str]:
    findings: list[str] = []
    docs = [
        (SKILL_ROOT, [SKILL_ROOT / "SKILL.md", *sorted((SKILL_ROOT / "references").glob("*.md"))]),
        (DEV_ROOT, [*sorted((DEV_ROOT / "evals").glob("*.md")), DEV_ROOT / "IMPROVEMENT_PLAN.md", DEV_ROOT / "LEADING_SKILLS_COMPARISON.md", DEV_ROOT / "research.md"]),
    ]
    for base, paths in docs:
        for path in paths:
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            for m in LOCAL_LINK_RE.finditer(text):
                target = m.group(1).split("#", 1)[0]
                if not target or re.match(r"^[a-z]+://", target) or target.startswith("mailto:"):
                    continue
                if target.startswith("/"):
                    continue
                resolved = (path.parent / target).resolve()
                try:
                    resolved.relative_to(base.resolve())
                except ValueError:
                    continue
                if not resolved.exists():
                    findings.append(f"P1 {path.relative_to(base)}:{line_for(text, m.start())}: broken local link -> {m.group(1)}")
    return findings


def check_line_count() -> list[str]:
    skill = SKILL_ROOT / "SKILL.md"
    if not skill.exists():
        return ["P0 SKILL.md: missing"]
    lines = skill.read_text(encoding="utf-8").count("\n") + 1
    findings = []
    if lines > 500:
        findings.append(f"P0 SKILL.md: hard max exceeded ({lines} lines > 500)")
    elif lines > 350:
        findings.append(f"P1 SKILL.md: router target exceeded ({lines} lines > 350 target)")
    return findings


def main() -> int:
    global SKILL_ROOT
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-p1", action="store_true", help="exit 0 when only P1 findings remain")
    parser.add_argument("--skill-root", default=str(DEFAULT_SKILL_ROOT), help="path to installable skill root containing SKILL.md")
    args = parser.parse_args()
    SKILL_ROOT = Path(args.skill_root).resolve()

    p0 = check_patterns(P0_PATTERNS, "P0")
    p1 = check_patterns(P1_PATTERNS, "P1") + check_links() + check_line_count()

    print(f"P0 findings: {len(p0)}")
    for item in p0:
        print(f"- {item}")
    print(f"\nP1 findings: {len(p1)}")
    for item in p1:
        print(f"- {item}")

    if p0:
        return 1
    if p1 and not args.allow_p1:
        return 1
    print("\nOK: static audit passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
