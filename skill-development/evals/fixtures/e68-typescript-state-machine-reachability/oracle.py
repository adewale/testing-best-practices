#!/usr/bin/env python3
"""E68 oracle: command caps are not evidence of reachable state transitions."""
from __future__ import annotations

import re
import sys
from pathlib import Path

NEGATED = re.compile(
    r"(?:\b(?:do|does|did|should|must|need|can|could|will|would)\s+not\b"
    r"|\b(?:don.t|doesn.t|didn.t|shouldn.t|mustn.t|needn.t|can.t|cannot|"
    r"couldn.t|won.t|wouldn.t)\b|\bnot\b|\bnever\b|\bwithout\b|\bno\s+need\s+to\b)"
    r"(?:\W+\w+){0,6}\W*$",
    re.IGNORECASE,
)


def read_markdown(root: Path) -> str:
    return "\n".join(p.read_text(errors="ignore") for p in root.rglob("*.md"))


def has(pattern: str, text: str) -> bool:
    return re.search(pattern, text, re.IGNORECASE | re.DOTALL) is not None


def negated_before(text: str, start: int) -> bool:
    prefix = text[max(0, start - 140) : start]
    prefix = re.split(r"(?<=[.!?;])\s+", prefix)[-1]
    return NEGATED.search(prefix) is not None


def affirmed(pattern: str, text: str) -> bool:
    return any(
        not negated_before(text, match.start())
        for match in re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
    )


def affirmed_predicate_after(subject: str, predicate: str, text: str, distance: int = 180) -> bool:
    for subject_match in re.finditer(subject, text, re.IGNORECASE | re.DOTALL):
        tail = text[subject_match.end() : subject_match.end() + distance]
        for predicate_match in re.finditer(predicate, tail, re.IGNORECASE | re.DOTALL):
            start = subject_match.end() + predicate_match.start()
            if not negated_before(text, start):
                return True
    return False


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    low = read_markdown(root).lower()
    errors: list[str] = []
    if not low.strip():
        print("no markdown assessment found", file=sys.stderr)
        return 1

    generation_independent = has(
        r"fc\.commands.{0,180}(?:draw|generate|produce).{0,180}"
        r"(?:independent|does not|doesn.t).{0,180}(?:check|precondition)"
        r"|fc\.commands.{0,180}(?:independent|does not|doesn.t).{0,180}"
        r"(?:check|precondition)",
        low,
    )
    check_evaluation = has(
        r"(?:asyncmodelrun|modelrun).{0,180}(?:evaluate|call|apply|use).{0,120}"
        r"(?:check|precondition).{0,180}(?:skip|discard|not run|false)"
        r"|(?:during|under).{0,30}(?:asyncmodelrun|modelrun).{0,180}"
        r"(?:check|precondition).{0,180}(?:skip|discard|not run|false)",
        low,
    )
    if not (generation_independent and check_evaluation):
        errors.append("does not explain fc.commands generation and check/asyncModelRun skip semantics")

    incorrect_generation_claim = affirmed_predicate_after(
        r"fc\.commands",
        r"(?:generate|draw|produce)s?.{0,80}only.{0,100}"
        r"(?:commands?.{0,40}(?:whose )?check passes|applicable|admissible)"
        r"|(?:consult|use|call|evaluate)s?.{0,60}check"
        r".{0,80}(?:during|before).{0,60}generation",
        low,
    ) or affirmed_predicate_after(
        r"(?:check|precondition)s?",
        r"(?:filter|control|constrain|prune|restrict|limit|select)\w*.{0,100}"
        r"(?:generation|generated (?:command )?(?:sequence|list|commands?))",
        low,
    ) or affirmed(
        r"\bonly\s+draws?\s+commands?\s+whose\s+checks?\s+pass",
        low,
    )
    if incorrect_generation_claim:
        errors.append("incorrectly claims Command.check constrains fc.commands generation")

    early_return = has(
        r"(early return|return.{0,40}run|inside run).{0,180}(hide|no.?op|vacu|admiss|precondition)"
        r"|(pass|passes).{0,60}check.{0,100}return.{0,80}(without|no.?op|touch)"
        r"|run.{0,100}(silently|early).{0,40}return.{0,140}(unless|target|uuid|id)"
        r"|(coarse|weak|wrong).{0,100}check.{0,160}(m\.users|selected|id|target)",
        low,
    )
    exact_check = affirmed(
        r"\b(move|put|encode|require|restrict|change|set|update|rewrite|make)\b.{0,160}"
        r"(exact|target-specific|m\.users\.has|users\.has|id.{0,30}selected).{0,120}check"
        r"|\b(move|put|encode|require|restrict|change|set|update|rewrite|make)\b"
        r".{0,120}check.{0,160}"
        r"(exact|target-specific|m\.users\.has|users\.has|id.{0,30}selected)",
        low,
    )
    if not early_return:
        errors.append("misses that target-specific preconditions are hidden as no-op early returns in run")
    if not exact_check:
        errors.append("does not move exact target admissibility into each command's check")

    measured = affirmed(
        r"\b(instrument|measure|count|record|observe|report|track|threshold)\b"
        r"[^.!?;]{0,180}"
        r"(accepted|effective|executed|real)[^.!?;]{0,100}(transition|command|call)"
        r"|\b(instrument|measure|count|record|observe|report|track|threshold)\b"
        r"[^.!?;]{0,180}"
        r"(transition|command|call)[^.!?;]{0,100}(accepted|effective|executed|real)",
        low,
    ) and has(r"(maxcommands|max commands|100).{0,140}(cap|not|upper|does not|isn.t)", low)
    if not measured:
        errors.append("does not replace the maxCommands multiplication with accepted/effective transition metrics")

    replay_artifacts = has(r"seed.{0,160}path|path.{0,160}seed", low) and "replaypath" in low
    replay_action = affirmed(
        r"\b(pass|preserve|capture|record|report|read|store|configure|wire|set|use|provide)\b"
        r".{0,200}"
        r"(seed|path|replaypath)",
        low,
    )
    propagation = affirmed(
        r"\b(propagate|forward|pass|inject)\b.{0,140}"
        r"(vitest|project|worker|sandbox|process\.env|fc_seed)",
        low,
    ) or affirmed(
        r"\b(?:ensur\w*|verify|make sure)\b.{0,180}"
        r"(?:vitest|project|worker|sandbox).{0,120}"
        r"(?:receive|inherit|see|obtain|get|have)s?\b.{0,100}"
        r"(?:seed|path|replay|value)",
        low,
    )
    replay = replay_artifacts and replay_action and propagation
    if not replay:
        errors.append("does not add seed+path+commands replayPath replay and propagate it through Vitest projects/workers")

    if affirmed_predicate_after(
        r"200\s*[×x*]\s*100", r"\b(means|proves|equals|=)\b.{0,80}20.?000", low
    ):
        errors.append("accepts the generated cap as 20,000 executed transitions")
    if affirmed_predicate_after(
        r"\b(increase|raise)\b.{0,50}maxcommands", r"\b(fix|solve|enough|coverage)\b", low
    ):
        errors.append("uses a higher maxCommands cap as the reachability fix")
    if affirmed_predicate_after(
        r"date\.now", r"\b(good|reproducible|sufficient)\b", low
    ):
        errors.append("claims Date.now provides reproducible failure replay")
    if affirmed_predicate_after(
        r"\b(keep|leave)\b.{0,80}(early return|return in run)",
        r"\b(fine|correct|acceptable)\b",
        low,
    ):
        errors.append("accepts hidden no-op preconditions in run")

    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
