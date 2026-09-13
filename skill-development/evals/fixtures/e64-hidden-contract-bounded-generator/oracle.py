#!/usr/bin/env python3
"""E64 restraint oracle: generator constraints that track a documented contract
must not be labelled over-constrained, nor widened past the contract."""
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


def read(root: Path, ext: str) -> str:
    return "\n".join(p.read_text(errors="ignore") for p in root.rglob(f"*.{ext}"))


def negated_before(text: str, start: int) -> bool:
    prefix = text[max(0, start - 140) : start]
    prefix = re.split(r"(?<=[.!?;])\s+", prefix)[-1]
    return NEGATED.search(prefix) is not None


def affirmed(pattern: str, text: str) -> bool:
    return any(
        not negated_before(text, match.start())
        for match in re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
    )


def affirmed_predicate_after(
    subject: str, predicate: str, text: str, distance: int = 180
) -> bool:
    for subject_match in re.finditer(subject, text, re.IGNORECASE | re.DOTALL):
        tail = text[subject_match.end() : subject_match.end() + distance]
        for predicate_match in re.finditer(predicate, tail, re.IGNORECASE | re.DOTALL):
            start = subject_match.end() + predicate_match.start()
            if not negated_before(text, start):
                return True
    return False


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    low = read(root, "md").lower()
    errors = []

    # Any affirmative recommendation to cross the documented domain is a
    # failure. Polarity matters: "do not remove min_size" is correct advice.
    demands_widening = affirmed(
        r"\b(remove|drop|delete|relax|widen|loosen)\b[^.\n]{0,80}"
        r"(min_size|allow_nan|allow_infinity|constraint|bound|generator|domain)"
        r"|\b(set|change|turn)\b[^.\n]{0,60}allow[_ ]nan[^.\n]{0,30}true",
        low,
    )
    discards_all_bounds = re.search(
        r"\b(?:keep|retain|preserve)\s+none\b[^.\n]{0,120}"
        r"(?:constraints?|bounds?|generator)"
        r"|\b(?:all|these|those|the)\s+(?:generator\s+)?(?:constraints?|bounds?)"
        r"\s+(?:should|must|need(?:s)? to)\s+(?:go|be\s+(?:removed|dropped|deleted))",
        low,
        re.IGNORECASE,
    )
    includes_out_of_contract_values = affirmed(
        r"\b(?:include|admit|add|generate|sample|cover|exercise)\b[^.!?\n]{0,120}"
        r"(?:empty (?:lists?|inputs?)|nan|infinity|infinite|non-?finite)"
        r"[^.!?\n]{0,120}(?:this|the|same|current) (?:generator|strategy|property)"
        r"|\b(?:this|the|same|current) (?:generator|strategy|property)\b"
        r"[^.!?\n]{0,120}"
        r"(?:include|admit|add|generate|sample|cover|exercise)\w*\b[^.!?\n]{0,120}"
        r"(?:empty (?:lists?|inputs?)|nan|infinity|infinite|non-?finite)",
        low,
    )
    rejects_preservation = re.search(
        r"\b(?:keep|retain|preserve|leave)\b[^.!?\n]{0,80}\?\s*"
        r"(?:no|not\b|never\b)",
        low,
        re.IGNORECASE,
    )
    if (
        demands_widening
        or discards_all_bounds
        or includes_out_of_contract_values
        or rejects_preservation
    ):
        errors.append(
            "over-applied generator discipline: demanded widening past the "
            "documented contract"
        )

    nonempty_contract = re.search(
        r"(min_size|non-?empty|empty).{0,140}(contract|document|spec|require|valueerror)"
        r"|(contract|document|spec|require).{0,140}(min_size|non-?empty|empty)",
        low,
        re.DOTALL,
    )
    finite_contract = re.search(
        r"(nan|infinit|finite).{0,140}(contract|document|spec|undefined|exclude)"
        r"|(contract|document|spec|undefined|exclude).{0,140}(nan|infinit|finite)",
        low,
        re.DOTALL,
    )
    if not (nonempty_contract and finite_contract):
        errors.append("does not map both size and finite-float bounds to the documented contract")

    preserves_bounds = affirmed(
        r"\b(keep|retain|preserve|leave)\b[^.\n]{0,100}"
        r"(generator|constraint|bound|min_size|allow_nan|allow_infinity)",
        low,
    ) or affirmed_predicate_after(
        r"\b(?:generator|strategy|constraints?|bounds?|domain)\b",
        r"\b(?:appropriate|correct|sound|valid|well[- ]scoped|as written|"
        r"should (?:stay|remain)|can (?:stay|remain))\b",
        low,
    ) or re.search(
        r"\b(?:do not|don.t|should not|must not|never)\b[^.\n]{0,50}"
        r"(?:remove|drop|widen|relax|loosen)\b[^.\n]{0,80}"
        r"(min_size|allow_nan|allow_infinity|constraint|bound)",
        low,
    )
    if not preserves_bounds:
        errors.append("does not explicitly preserve the contract-derived generator bounds")

    useful_improvement = re.search(
        r"empty.{0,100}valueerror|valueerror.{0,100}empty"
        r"|stronger.{0,100}(property|invariant|oracle)"
        r"|(independent|counting|order statistic).{0,100}(property|invariant|oracle|median)",
        low,
        re.DOTALL,
    )
    if not useful_improvement:
        errors.append("does not identify the specified empty-list path or the weak median oracle")
    if len(low.strip()) < 80:
        errors.append("empty assessment")

    for e in errors:
        print(e, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
