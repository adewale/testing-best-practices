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
        (r"(do not|don.?t|should not|must not|is not|isn.?t).{0,90}(restore|back above|70%|score.{0,25}(goal|target|objective)|round[- ]number floor)|(score|number).{0,50}(is not|isn.?t|should not be).{0,30}(goal|correctness|target)|(?:round[- ]number floor|70%).{0,60}(?:not|isn.?t).{0,35}(?:acceptance|primary).{0,15}(?:criterion|gate|target)", "does not explicitly reject score restoration as the objective"),
        (r"equivalent|redundant|unkillable", "does not independently consider equivalent/redundant survivors"),
        (r"like[- ]for[- ]like|same (scope|operator|config)|denominator|scope.{0,40}(change|tripl)|comparable", "does not require a comparable scope/operator/denominator"),
        (r"surviv.{0,100}(timeout|compile|infrastructure|no[- ]coverage)|(?:timeout|compile|infrastructure|no[- ]coverage).{0,100}surviv|distinct status|separate.{0,40}status", "does not separate actual survivors from incomplete/tool statuses"),
        (r"triage|classif|representative survivor|inspect.{0,30}(entry|surviv)", "does not triage representative survivors"),
        (r"behavior|regression|property|dead code|remove.{0,20}code|actionable", "does not turn triage into behavior/code decisions"),
    ]
    for pattern, message in checks:
        if not re.search(pattern, text, re.S): errors.append(message)
    if re.search(r"do not challenge|don.?t challenge", text):
        errors.append("negates the required challenge to score restoration")
    negated_obligations = [
        (r"(?:do not|don.?t|never)\s+(?:consider|classify|triage|inspect)\b.{0,30}(?:equivalent|redundant)|(?:equivalent|redundant)(?: mutants?| survivors?).{0,20}(?:are |is )?(?:irrelevant|unnecessary|not relevant)", "negates equivalent/redundant survivor triage"),
        (r"(?:do not|don.?t|never)\s+(?:separate|distinguish)\b.{0,45}(?:status|timeout|surviv)|(?:status|timeout).{0,35}(?:need not|should not).{0,20}separate", "negates survivor/status separation"),
        (r"(?:do not|don.?t|never|skip)\s+(?:the )?(?:representative )?(?:triage|classification|inspection)\b", "negates representative triage"),
        (r"(?:behavior|regression|property)(?: tests?)?.{0,25}(?:are |is )?(?:unnecessary|not needed|irrelevant)|(?:do not|don.?t)\s+(?:add|write)\b.{0,25}(?:behavior|regression|property)", "negates behavior/code decisions"),
    ]
    for pattern, message in negated_obligations:
        if re.search(pattern, text, re.S): errors.append(message)
    if re.search(r"break\s*:?\s*70|stop.{0,25}(at|above)\s*70|kill.{0,40}(all|until).{0,20}70|(?:make|use|set).{0,35}70%.{0,35}(?:acceptance|required).{0,15}(?:threshold|gate|target)|70%.{0,35}(?:acceptance|required) threshold", text, re.S):
        errors.append("uses 70 as the acceptance target")
    for error in errors: print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
