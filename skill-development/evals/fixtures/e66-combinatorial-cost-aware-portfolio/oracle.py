#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

DELETE = r"(?:delete|deletes|deleted|deleting|remove|removes|removed|removing|drop|drops|dropped|dropping|discard|discards|discarded|discarding)"
REGRESSION = r"(?:known|fixed|repaired|safari|four[- ]way|4[- ]way|high[- ]order).{0,35}(?:regression|fault|case|test|row)|(?:regression|repaired fault).{0,35}(?:known|fixed|safari|four[- ]way|4[- ]way|high[- ]order)"


def deletes_known_regression(text: str) -> bool:
    clauses = [part.strip() for part in re.split(r"[.;!?\n]+", text) if part.strip()]
    named_target = r"(?:known|fixed|safari|four[- ]way|4[- ]way|high[- ]order).{0,35}(?:regression|fault|case|test|row)"
    prior_regression = False
    for clause in clauses:
        names_regression = bool(re.search(REGRESSION, clause))
        deletes = bool(re.search(rf"\b{DELETE}\b", clause))
        negated = bool(re.search(rf"(?:do not|don.?t|must not|should not|never)\s+{DELETE}\b", clause))
        direct = bool(
            re.search(rf"\b{DELETE}\b.{0,45}{named_target}|{named_target}.{0,45}\b{DELETE}\b", clause)
        )
        anaphoric = bool(
            re.search(rf"\b{DELETE}\s+(?:it|this|that|the)(?:\s+(?:case|test|row|regression))?\b", clause)
            or re.search(rf"(?:the\s+)?(?:case|test|row|regression).{0,20}(?:can|should|may|must|will|is|be).{0,12}\b{DELETE}\b", clause)
        )
        if deletes and not negated and (direct or (prior_regression and anaphoric)):
            return True
        prior_regression = names_regression
    return False


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    text = "\n".join(path.read_text(errors="ignore") for path in root.rglob("*.md"))
    text = text.lower().replace("*", "").replace("`", "").split("acceptance-report", 1)[0]
    errors: list[str] = []
    checks = [
        (
            r"canonical registry|registry.{0,50}(source of truth|exact|one[- ]way)|exact[- ]set|exact one[- ]way",
            "missing exact canonical-registry enrollment",
        ),
        (
            r"(?:keep(?!\s+in mind)|retain|preserve|must remain|do not delete|don.?t delete).{0,70}(?:known|fixed|repaired|regression|four[- ]way|4[- ]way)|(?:known|fixed|repaired|four[- ]way|4[- ]way).{0,70}(?:keep|retain|preserve|mandatory fixed)",
            "does not affirmatively preserve the known high-order regression test",
        ),
        (
            r"exhaust.{0,60}(cheap|small|finite|pure|schema|registry)|enumerat.{0,60}(cheap|pure|schema|registry)",
            "missing exhaustive cheap slices",
        ),
        (
            r"constrain.{0,80}(pairwise|2[- ]way)|(pairwise|2[- ]way).{0,80}constrain",
            "missing constrained pairwise base",
        ),
        (
            r"(?:variable[- ]strength|3[- ]way|three[- ]way|higher strength).{0,120}(?:family|look|palette|security|transparency|named|risk)|(family|look|palette|security|transparency).{0,120}(?:3[- ]way|three[- ]way|variable[- ]strength)",
            "missing a named elevated high-risk factor group",
        ),
        (r"browser|hosted|boundary", "does not address expensive boundaries"),
    ]
    for pattern, message in checks:
        if not re.search(pattern, text, re.DOTALL):
            errors.append(message)

    contradictions = [
        (
            r"(?:do not|don.?t|never|not to)\s+(?:keep|retain|preserve)\b.{0,45}regression|regression.{0,30}(?:not required|unnecessary|optional)",
            "negates retention of the known regression",
        ),
        (
            r"(?:do not|don.?t|never|skip)\s+(?:exhaust|enumerate)\b.{0,45}(?:cheap|pure|schema|registry)",
            "negates exhaustive cheap slices",
        ),
        (
            r"(?:do not|don.?t|never)\s+(?:use|generate|require)\b.{0,35}(?:constrained pairwise|pairwise)",
            "negates constrained pairwise coverage",
        ),
        (
            r"(?:do not|don.?t|never)\s+(?:use|add|require)\b.{0,35}(?:variable[- ]strength|3[- ]way|three[- ]way)",
            "negates the elevated risk group",
        ),
        (
            r"(?:do not|don.?t|never|skip)\s+(?:run |use )?(?:the )?(?:old/new )?shadow\b",
            "negates shadow validation",
        ),
        (
            r"(?:do not|don.?t|never|skip)\s+(?:use|run)?\s*(?:mutation|sabotage|seeded fault)|(?:mutation|sabotage).{0,25}(?:unnecessary|not required)",
            "negates fault-evidence validation",
        ),
        (
            r"skip.{0,30}validation.{0,35}before.{0,20}(?:delet|remov|replac)|(?:delet|remov|replac).{0,35}before.{0,25}validation",
            "permits deletion before validation",
        ),
    ]
    for pattern, message in contradictions:
        if re.search(pattern, text, re.DOTALL):
            errors.append(message)

    cost_groups = [
        bool(re.search(r"critical path|wall[- ]clock|runtime|runner|cpu", text)),
        bool(re.search(r"setup|startup|environment|fixture reuse", text)),
        bool(re.search(r"flake|false[- ]red|rerun|retr(?:y|ies)", text)),
        bool(re.search(r"maintenance|baseline review|review cost|churn", text)),
        bool(re.search(r"triage|diagnos|localization", text)),
    ]
    if sum(cost_groups) < 3:
        errors.append("does not compare at least three heterogeneous cost classes")
    if not re.search(r"shadow|run (?:the )?old.{0,30}(?:and|with).{0,20}(?:new|proposed)|old/new", text, re.DOTALL):
        errors.append("does not require old/new shadow validation")
    if not re.search(r"mutation|sabotage|seeded fault|inject.{0,50}fake.{0,80}(?:fail|broken)|fake registry member.{0,80}(?:fail|broken)", text, re.DOTALL):
        errors.append("does not require mutation/sabotage fault evidence")
    if not re.search(r"before.{0,50}(?:delet|remov|replac)|(?:delet|remov|replac).{0,50}(?:only after|after shadow|after replay)", text, re.DOTALL):
        errors.append("does not make validation a precondition for test deletion/replacement")
    if deletes_known_regression(text):
        errors.append("deletes the mandatory known regression despite mentioning retention or validation")

    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
