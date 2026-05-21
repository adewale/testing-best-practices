#!/usr/bin/env python3
"""Score an installable testing-best-practices skill artifact.

This is a static version-quality rubric. It intentionally complements prompt
fixture oracles: when prompt outputs saturate, this catches whether the skill
itself contains calibrated, complete, non-contradictory guidance.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Check:
    category: str
    name: str
    points: float
    kind: str
    path: str | None = None
    pattern: str | None = None
    max_lines: int | None = None


def read(root: Path, rel: str) -> str:
    path = root / rel
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def exists(root: Path, rel: str) -> bool:
    return (root / rel).exists()


def all_text(root: Path) -> str:
    parts = []
    for path in [root / "SKILL.md", *sorted((root / "references").glob("*.md"))]:
        if path.exists():
            parts.append(path.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(parts)


CHECKS: list[Check] = [
    # A. Router/usability 15
    Check("A router/usability", "SKILL.md <=350 lines", 3, "line_max", "SKILL.md", max_lines=350),
    Check("A router/usability", "mode workflows for write/assess/upgrade/detect", 3, "contains", "SKILL.md", r"Write.*Assess.*Upgrade.*Detect|write.*assess.*upgrade.*detect"),
    Check("A router/usability", "first-context checklist", 3, "contains", "SKILL.md", r"First 90 seconds|adjacent tests|runner commands|Detect language"),
    Check("A router/usability", "reference matrix / lazy loading", 3, "contains", "SKILL.md", r"Reference matrix|Load these ONLY|Topical references"),
    Check("A router/usability", "final report/validation contract", 3, "contains", "SKILL.md", r"Final report|Commands run|Gaps / risks|Validation loop"),

    # B. Static safety/calibration 25
    Check("B safety/calibration", "no weak toBeDefined PBT example", 3, "not_contains", "references/typescript.md", r"expect\(result\)\.toBeDefined\(\)"),
    Check("B safety/calibration", "no six/seven contradiction", 2, "not_contains", "references/correctness-by-construction.md", r"In all six cases"),
    Check("B safety/calibration", "VCR vs MSW distinction", 3, "not_contains", "references/vcr-cassettes.md", r"## TypeScript \(msw\)"),
    Check("B safety/calibration", "integration not external-only", 3, "not_contains", "references/antipatterns.md", r"An integration test must have at least one real\s+external dependency"),
    Check("B safety/calibration", "positive+negative rule scoped", 3, "not_contains", "SKILL.md", r"Every test should verify what SHOULD be present"),
    Check("B safety/calibration", "no unsafe downstream deletion wording", 3, "not_contains", "SKILL.md", r"delete the downstream checks \*\*and their tests\*\*"),
    Check("B safety/calibration", "TDD evidence/feasibility calibrated", 3, "contains", "SKILL.md", r"cannot run|cannot.*red|evidence|feasible|when feasible"),
    Check("B safety/calibration", "assertion count calibrated", 3, "contains", "SKILL.md", r"heuristic, not a law|property test.*one.*oracle|table.*one.*oracle|exception test"),
    Check("B safety/calibration", "Go table-driven guidance not universal", 2, "not_contains", "references/go.md", r"Every test should use this"),

    # C. Language coverage 15
    Check("C language coverage", "Python reference exists", 3, "exists", "references/python.md"),
    Check("C language coverage", "TypeScript reference exists", 3, "exists", "references/typescript.md"),
    Check("C language coverage", "Go reference exists", 3, "exists", "references/go.md"),
    Check("C language coverage", "Rust reference exists", 3, "exists", "references/rust.md"),
    Check("C language coverage", "unsupported-language fallback", 3, "contains", "SKILL.md", r"unsupported.*language|language is unsupported|project conventions"),

    # D. Technique breadth 20
    Check("D technique breadth", "deterministic time", 2, "exists", "references/deterministic-time.md"),
    Check("D technique breadth", "characterization testing", 2, "exists", "references/characterization-testing.md"),
    Check("D technique breadth", "differential/conformance testing", 2, "exists", "references/differential-testing.md"),
    Check("D technique breadth", "golden/snapshot testing", 2, "exists", "references/golden-file-testing.md"),
    Check("D technique breadth", "doc-sync testing", 2, "exists", "references/doc-sync-testing.md"),
    Check("D technique breadth", "exhaustive testing", 2, "exists", "references/exhaustive-testing.md"),
    Check("D technique breadth", "mathematical properties", 2, "exists", "references/mathematical-properties.md"),
    Check("D technique breadth", "mutation testing", 2, "exists", "references/mutation-testing.md"),
    Check("D technique breadth", "test data builders", 2, "exists", "references/test-data-builders.md"),
    Check("D technique breadth", "VCR/recorded fixtures", 2, "exists", "references/vcr-cassettes.md"),

    # E. Correctness-by-construction 15
    Check("E correctness-by-construction", "dedicated correctness-by-construction reference", 3, "exists", "references/correctness-by-construction.md"),
    Check("E correctness-by-construction", "deletion safety preconditions", 4, "contains_any", None, r"trust boundary|non-adversarial|boundary tests|hostile input|approved"),
    Check("E correctness-by-construction", "Go zero-value caveat", 3, "contains", "references/correctness-by-construction.md", r"zero value|var e Email"),
    Check("E correctness-by-construction", "scope control for production type changes", 3, "contains", "SKILL.md", r"do not change production|tests only|in scope|approved"),
    Check("E correctness-by-construction", "preserves real defense-in-depth", 2, "contains_any", None, r"different failure mode|different adversary|auth|security boundaries|external-failure"),

    # F. Validation/reporting 10
    Check("F validation/reporting", "validation loop", 3, "contains", "SKILL.md", r"Validation loop|After writing|Run the nearest"),
    Check("F validation/reporting", "reports commands/results/gaps", 3, "contains", "SKILL.md", r"Commands run|Results|Gaps|blocked validation"),
    Check("F validation/reporting", "mutation/gap analysis guidance", 2, "exists", "references/mutation-testing.md"),
    Check("F validation/reporting", "anti-sabotage checks", 2, "contains", "SKILL.md", r"skip|test\.only|logging-not-asserting|assertion-free|sleep"),
]


def check(root: Path, c: Check) -> tuple[bool, str]:
    target_text = all_text(root) if c.kind == "contains_any" else read(root, c.path or "")
    if c.kind == "exists":
        ok = exists(root, c.path or "")
    elif c.kind == "contains":
        ok = bool(re.search(c.pattern or "", target_text, re.I | re.S))
    elif c.kind == "contains_any":
        ok = bool(re.search(c.pattern or "", target_text, re.I | re.S))
    elif c.kind == "not_contains":
        # Missing files do not get credit for absence; they are usually breadth gaps.
        ok = exists(root, c.path or "") and not bool(re.search(c.pattern or "", target_text, re.I | re.S))
    elif c.kind == "line_max":
        if not exists(root, c.path or ""):
            ok = False
        else:
            lines = read(root, c.path or "").count("\n") + 1
            ok = lines <= (c.max_lines or 999999)
            return ok, f"{lines} lines <= {c.max_lines}"
    else:
        raise ValueError(c.kind)
    return ok, "pass" if ok else "fail"


def score(root: Path) -> dict:
    details = []
    total = 0.0
    possible = 0.0
    by_cat: dict[str, dict[str, float]] = {}
    for c in CHECKS:
        ok, note = check(root, c)
        possible += c.points
        if ok:
            total += c.points
        cat = by_cat.setdefault(c.category, {"score": 0.0, "possible": 0.0})
        cat["possible"] += c.points
        if ok:
            cat["score"] += c.points
        details.append({"category": c.category, "name": c.name, "points": c.points, "passed": ok, "note": note})
    return {"score": round(total, 1), "possible": possible, "percent": round(total / possible * 100, 1), "categories": by_cat, "details": details}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-root", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = Path(args.skill_root).resolve()
    result = score(root)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"score: {result['score']}/{result['possible']} ({result['percent']}%)")
        for cat, vals in result["categories"].items():
            print(f"{cat}: {vals['score']}/{vals['possible']}")
        failed = [d for d in result["details"] if not d["passed"]]
        if failed:
            print("\nFailed checks:")
            for d in failed:
                print(f"- [{d['category']}] {d['name']} ({d['points']} pts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
