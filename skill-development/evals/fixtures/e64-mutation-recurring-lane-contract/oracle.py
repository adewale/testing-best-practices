#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    text = "\n".join(path.read_text(errors="ignore") for path in root.rglob("*.md"))
    text = text.lower().replace("*", "").replace("`", "").split("acceptance-report", 1)[0]
    errors: list[str] = []
    checks = [
        (
            r"(one[- ]?(shot|time)|manual|dispatch).{0,100}(complete|baseline|target.{0,20}ci)|(complete|baseline).{0,100}(before|prior).{0,40}(schedule|cron)",
            "no completed target-CI baseline required before scheduling",
        ),
        (
            r"(start|limit|scope|narrow|prefer|run).{0,70}(changed[- ]code|critical module)|(changed[- ]code|critical module).{0,70}(scope|lane|run)",
            "does not affirmatively narrow to changed/critical scope",
        ),
        (
            r"seeded|sabotage|repaired fault|killed|actionable mutant|named fault class|prove.{0,30}(bite|detect)",
            "does not require demonstrated fault-class/oracle bite",
        ),
        (r"owner|notify|notification|page|block", "no owner or notification/blocking path"),
        (
            r"timeout|runner[- ]minute|compute budget|runtime budget|capacity",
            "does not reconcile runtime with timeout/budget",
        ),
        (
            r"(reject|remove|omit|do not|don.?t|must not|no).{0,70}(break\s*:?\s*60|floor|threshold)|(break\s*:?\s*null)",
            "does not reject the copied unmeasured score floor",
        ),
        (
            r"(repeated|consecutive|three|3).{0,70}(operational|infrastructure|untriaged|fail|red).{0,100}(stop|disable|narrow|fix|delete)|(stop|disable|narrow).{0,80}(before|rather than).{0,30}(expand|scope)",
            "no stop-before-expansion rule for operational/untriaged failures",
        ),
    ]
    for pattern, message in checks:
        if not re.search(pattern, text, re.DOTALL):
            errors.append(message)

    contradictions = [
        (
            r"(?:target[- ]ci\s+)?(?:completion|baseline).{0,45}(?:irrelevant|optional|unnecessary|not required|after (?:the )?(?:schedule|cron)|later)",
            "makes the completed target-CI baseline optional or post-schedule",
        ),
        (
            r"(?:schedule|enable|start|launch).{0,45}(?:immediately|now|as[- ]is|before (?:the )?baseline)",
            "schedules the lane before its prerequisites are met",
        ),
        (
            r"(?:expand|widen|start).{0,45}(?:repository[- ]wide|whole repository).{0,30}(?:immediately|now|from the start)|(?:repository[- ]wide|whole repository).{0,45}(?:immediately|from the start)",
            "expands to repository-wide scope before proving the focused lane",
        ),
        (
            r"(?:owner\s+(?:is\s+)?tbd|no owner (?:is )?required|owner.{0,20}(?:unnecessary|not required)|notify nobody|do not notify|don.?t notify)",
            "leaves the recurring lane unowned or unnotified",
        ),
        (
            r"(?:not before|only after).{0,30}(?:expand|scope growth)|(?:expand|scope growth).{0,35}before.{0,20}(?:stop|fix|narrow|disable)",
            "allows scope growth before resolving repeated operational failures",
        ),
        (
            r"(?:completed |target[- ]ci )?baseline.{0,35}(?:not required|unnecessary|optional)|(?:do not|don.?t|never)\s+require.{0,25}baseline|no baseline (?:is )?required",
            "negates the completed baseline prerequisite",
        ),
        (r"(?:do not|don.?t|never)\s+narrow\b", "negates focused scope"),
        (
            r"(?:seeded sabotage|repaired fault|fault[- ]class bite|oracle bite).{0,25}(?:is |are )?(?:unnecessary|not required|irrelevant)|\bskip (?:the )?(?:seeded sabotage|fault[- ]class proof)",
            "negates demonstrated fault-class bite",
        ),
        (
            r"(?:do not|don.?t|never)\s+(?:stop|disable|narrow)\b.{0,45}(?:failure|red|before expansion)",
            "negates the operational stop rule",
        ),
    ]
    for pattern, message in contradictions:
        if re.search(pattern, text, re.DOTALL):
            errors.append(message)

    if re.search(
        r"(?:set|enforce|use|keep|require).{0,45}(?:break\s*:?\s*60|threshold.{0,15}60)|break\s*:?\s*60.{0,45}(?:every|all)",
        text,
        re.DOTALL,
    ):
        errors.append("retains or enforces break: 60 instead of rejecting the copied floor")

    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
