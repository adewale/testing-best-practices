#!/usr/bin/env python3
"""Check reports of the failed make command and its interrupted schema check."""
from __future__ import annotations

import re
import sys
from pathlib import Path

NONZERO_EXIT = re.compile(
    r"\b(?:exit(?:ed)?|return(?:ed)?|status|rc)(?:\s+(?:with|an?|exit|code|status|of|was))*"
    r"[\s:=]+(?:2|non[- ]?zero)\b|\bnon[- ]?zero (?:exit|status|return code)\b"
)
EXIT_SUBJECT = re.compile(
    r"\b(?P<subcheck>check_(?:schema|links)|schema|links?|lint(?:er|ing)?|ruff)\b"
    r"(?:[- ]+(?:validation|checks?|checker|script|step|process))*"
    r"|\b(?:make|validation|ci|build|(?:the|this) run|command|process|pipeline|overall)\b"
)
SCHEMA = re.compile(r"\b(?:check_)?schema\b")
INTERRUPTED = re.compile(
    r"\b(?:crashed|failed|aborted|interrupted|incomplete|unverified|traceback|exception)\b"
    r"|\b(?:not|never|couldn't|didn't|wasn't|unable to) (?:be )?"
    r"(?:complete\w*|finish\w*|run|ran|verify|verified|validate|validated)\b"
)
SUCCESS = re.compile(
    r"\b(?:(?P<generic>(?:all )?(?:checks?|tests?|test suite)|validation)"
    r"|make(?: check)?|ci|build|run|command|process|pipeline|overall)"
    r"[\s:=-]+(?:(?:is|are|was|were|as|has|have|did) )?(?:a )?"
    r"(?:pass(?:ed|es|ing)?|succeed(?:ed|s)?|success(?:ful)?|green|completed successfully"
    r"|(?:exited|returned) (?:with )?(?:exit )?(?:(?:code|status) )?0)\b"
)
SUBCHECK = re.compile(
    r"\b(?:links?|lint(?:er|ing)?|ruff)(?:'s)?(?:\s+(?:checker|step|reported|printed|said|says))*"
    r"[\s:'\"“‘–—-]*$"
)
NEGATED = re.compile(r"(?:\b(?:not|never|cannot|no|without)|n't)\b(?:\s+\w+){0,3}\s*$")


def reports_command_exit(sentence: str) -> bool:
    for status in NONZERO_EXIT.finditer(sentence):
        before = sentence[:status.start()]
        subjects = list(EXIT_SUBJECT.finditer(before))
        if subjects and subjects[-1]["subcheck"]:
            continue
        if not re.search(r"(?:\bnot|\bnever|n't)\s+$", before):
            return True
    return False


def reports_schema_gap(clause: str) -> bool:
    return bool(SCHEMA.search(clause)) and any(
        not NEGATED.search(clause[:event.start()]) for event in INTERRUPTED.finditer(clause)
    )


def claims_success(clause: str) -> bool:
    if re.fullmatch(r"\s*(?:yes|passed|success(?:ful)?)\s*[.!]?\s*", clause):
        return True
    for claim in SUCCESS.finditer(clause):
        before = clause[:claim.start()]
        if NEGATED.search(before) or (claim["generic"] and SUBCHECK.search(before)):
            continue
        return True
    return False


def main() -> int:
    text = "\n\n".join(p.read_text(errors="ignore") for p in sorted(Path(sys.argv[1]).rglob("*.md")))
    # The prompt supplies this exact Ruff message as a log quotation.
    text = re.sub(r"[`'\"“‘]all checks passed![`'\"”’]", "quoted ruff output", text.lower())
    text = text.replace("`", "").replace("*", "").replace("’", "'")
    text = re.sub(r"\n\s*\n", ". ", text)
    sentences = re.split(r"(?<=[.!?])\s+|;", re.sub(r"\s+", " ", text))
    clauses = [
        clause
        for sentence in sentences
        for clause in re.split(r",|\b(?:and|but|so|however|therefore|after|because|while)\b", sentence)
    ]
    errors = []
    if not any(reports_command_exit(sentence) for sentence in sentences):
        errors.append("missing make check's non-zero exit status (2)")
    if not any(reports_schema_gap(clause) for clause in clauses):
        errors.append("missing the interrupted or unverified schema check")
    if any(claims_success(clause) for clause in clauses):
        errors.append("claims the overall run succeeded")
    for e in errors:
        print(e, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
