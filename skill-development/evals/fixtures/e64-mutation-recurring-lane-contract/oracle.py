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
        (r"(one[- ]?(shot|time)|manual|dispatch).{0,100}(complete|baseline|target.{0,20}ci)|(complete|baseline).{0,100}(before|prior).{0,40}(schedule|cron)", "no completed target-CI baseline required before scheduling"),
        (r"(start|limit|scope|narrow|prefer|run).{0,70}(changed[- ]code|critical module)|(changed[- ]code|critical module).{0,70}(scope|lane|run)", "does not affirmatively narrow to changed/critical scope"),
        (r"seeded|sabotage|repaired fault|killed|actionable mutant|named fault class|prove.{0,30}(bite|detect)", "does not require demonstrated fault-class/oracle bite"),
        (r"owner|notify|notification|page|block", "no owner or notification/blocking path"),
        (r"timeout|runner[- ]minute|compute budget|runtime budget|capacity", "does not reconcile runtime with timeout/budget"),
        (r"(reject|remove|omit|do not|don.?t|must not|no).{0,70}(break\s*:?\s*60|floor|threshold)|(break\s*:?\s*null)", "does not reject the copied unmeasured score floor"),
        (r"(repeated|consecutive|three|3).{0,70}(operational|infrastructure|untriaged|fail|red).{0,100}(stop|disable|narrow|fix|delete)|(stop|disable|narrow).{0,80}(before|rather than).{0,30}(expand|scope)", "no stop-before-expansion rule for operational/untriaged failures"),
    ]
    for pattern, message in checks:
        if not re.search(pattern, text, re.S): errors.append(message)
    if re.search(r"(?:set|enforce|use|keep|require).{0,45}(?:break\s*:?\s*60|threshold.{0,15}60)|break\s*:?\s*60.{0,45}(?:every|all)", text, re.S):
        errors.append("retains or enforces break: 60 instead of rejecting the copied floor")
    negated_obligations = [
        (r"(?:completed |target[- ]ci )?baseline.{0,35}(?:not required|unnecessary|optional)|(?:do not|don.?t|never)\s+require.{0,25}baseline|no baseline (?:is )?required", "negates the completed baseline prerequisite"),
        (r"(?:do not|don.?t|never)\s+narrow\b", "negates focused scope"),
        (r"(?:seeded sabotage|repaired fault|fault[- ]class bite|oracle bite).{0,25}(?:is |are )?(?:unnecessary|not required|irrelevant)|\bskip (?:the )?(?:seeded sabotage|fault[- ]class proof)", "negates demonstrated fault-class bite"),
        (r"(?:no owner (?:is )?required|owner.{0,20}(?:is )?(?:unnecessary|not required)|do not notify|don.?t notify)", "negates ownership/notification"),
        (r"(?:do not|don.?t|never)\s+(?:stop|disable|narrow)\b.{0,45}(?:failure|red|before expansion)", "negates the operational stop rule"),
    ]
    for pattern, message in negated_obligations:
        if re.search(pattern, text, re.S): errors.append(message)
    for error in errors: print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
