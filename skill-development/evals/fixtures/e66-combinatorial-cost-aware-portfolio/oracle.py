#!/usr/bin/env python3
from __future__ import annotations
import re, sys
from pathlib import Path


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    text = "\n".join(p.read_text(errors="ignore") for p in root.rglob("*.md")).lower().replace("*", "").replace("`", "")
    text = text.split("acceptance-report", 1)[0]
    errors = []
    checks = [
        (r"canonical registry|registry.{0,50}(source of truth|exact|one[- ]way)|exact[- ]set|exact one[- ]way", "missing exact canonical-registry enrollment"),
        (r"known.{0,50}(regression|four|4[- ]way)|mandatory.{0,50}(regression|fixed)|(?:keep|retain).{0,50}regression", "does not preserve the known high-order regression"),
        (r"exhaust.{0,60}(cheap|small|finite|pure|schema|registry)|enumerat.{0,60}(cheap|pure|schema|registry)", "missing exhaustive cheap slices"),
        (r"constrain.{0,80}(pairwise|2[- ]way)|(pairwise|2[- ]way).{0,80}constrain", "missing constrained pairwise base"),
        (r"(?:variable[- ]strength|3[- ]way|three[- ]way|higher strength).{0,120}(?:family|look|palette|security|transparency|named|risk)|(family|look|palette|security|transparency).{0,120}(?:3[- ]way|three[- ]way|variable[- ]strength)", "missing a named elevated high-risk factor group"),
        (r"browser|hosted|boundary", "does not address expensive boundaries"),
        (r"pairwise.{0,120}(?:not|isn.?t|does not|cannot|miss).{0,50}(?:proof|correct|guarantee|higher|unmodel|replace|cover|sufficient)|not a correctness proof|(?:4[- ]way|four[- ]way).{0,80}(?:outside|absent|missing).{0,50}(?:pairwise|base|generated)|(?:known|fixed).{0,100}(?:4[- ]way|four[- ]way|four[- ]factor).{0,120}(?:pairwise|covering array|generated)|(?=.*pairwise)(?=.*(?:4[- ]way|four[- ]way|four[- ]factor))(?=.*(?:fixed|preserv))", "does not state pairwise's residual risk"),
    ]
    for pattern, message in checks:
        if not re.search(pattern, text, re.S): errors.append(message)

    negated_obligations = [
        (r"(?:do not|don.?t|never|not to)\s+(?:keep|retain|preserve)\b.{0,45}regression|regression.{0,30}(?:not required|unnecessary|optional)", "negates retention of the known regression"),
        (r"(?:do not|don.?t|never|skip)\s+(?:exhaust|enumerate)\b.{0,45}(?:cheap|pure|schema|registry)", "negates exhaustive cheap slices"),
        (r"(?:do not|don.?t|never)\s+(?:use|generate|require)\b.{0,35}(?:constrained pairwise|pairwise)", "negates constrained pairwise coverage"),
        (r"(?:do not|don.?t|never)\s+(?:use|add|require)\b.{0,35}(?:variable[- ]strength|3[- ]way|three[- ]way)", "negates the elevated risk group"),
        (r"(?:do not|don.?t|never|skip)\s+(?:run |use )?(?:the )?(?:old/new )?shadow\b", "negates shadow validation"),
        (r"(?:do not|don.?t|never|skip)\s+(?:use|run)?\s*(?:mutation|sabotage|seeded fault)|(?:mutation|sabotage).{0,25}(?:unnecessary|not required)", "negates fault-evidence validation"),
        (r"skip.{0,30}validation.{0,35}before.{0,20}(?:delet|remov|replac)|(?:delet|remov|replac).{0,35}before.{0,25}validation", "permits deletion before validation"),
    ]
    for pattern, message in negated_obligations:
        if re.search(pattern, text, re.S): errors.append(message)

    cost_groups = [
        bool(re.search(r"critical path|wall[- ]clock|runtime|runner|cpu", text)),
        bool(re.search(r"setup|startup|environment|fixture reuse", text)),
        bool(re.search(r"flake|false[- ]red|rerun|retr(?:y|ies)", text)),
        bool(re.search(r"maintenance|baseline review|review cost|churn", text)),
        bool(re.search(r"triage|diagnos|localization", text)),
    ]
    if sum(cost_groups) < 3:
        errors.append("does not compare at least three heterogeneous cost classes")
    if not re.search(r"shadow|run (?:the )?old.{0,30}(?:and|with).{0,20}(?:new|proposed)|old/new", text, re.S):
        errors.append("does not require old/new shadow validation")
    if not re.search(r"mutation|sabotage|seeded fault|inject.{0,50}fake.{0,80}(?:fail|broken)|fake registry member.{0,80}(?:fail|broken)", text, re.S):
        errors.append("does not require mutation/sabotage fault evidence")
    if not re.search(r"before.{0,50}(?:delet|remov|replac)|(?:delet|remov|replac).{0,50}(?:only after|after shadow|after replay)", text, re.S):
        errors.append("does not make validation a precondition for test deletion/replacement")

    for error in errors: print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
