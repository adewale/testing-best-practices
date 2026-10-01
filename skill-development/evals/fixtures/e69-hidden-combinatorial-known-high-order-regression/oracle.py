#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

DELETE = r"(?:delete|deletes|deleted|deleting|remove|removes|removed|removing|drop|drops|dropped|dropping|discard|discards|discarded|discarding)"
REGRESSION = r"(?:regression|repaired fault|known.{0,20}(?:case|test|fault)|safari.{0,35}(?:png|font|transparent)|four[- ]way|4[- ]way|high[- ]order)"


def retention_clause(clause: str) -> bool:
    retains = re.search(
        r"\b(?:retain|preserve|keep(?!\s+in mind))\b.{0,100}(?:test|case|row|regression)|(?:test|case|row|regression).{0,100}(?:must remain|retain|preserve|keep)",
        clause,
    )
    negates = re.search(r"(?:do not|don.?t|never|not to)\s+(?:keep|retain|preserve)\b", clause)
    documentation_only = re.search(r"(?:keep|retain|preserve).{0,25}(?:documented|documentation|note|record)", clause)
    return bool(retains and not negates and not documentation_only)


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    text = "\n".join(path.read_text(errors="ignore") for path in root.rglob("*.md"))
    text = text.lower().replace("*", "").replace("`", "").split("acceptance-report", 1)[0]
    clauses = [part.strip() for part in re.split(r"[.;!?\n]+", text) if part.strip()]
    regression_clauses = [clause for clause in clauses if re.search(REGRESSION, clause)]
    errors: list[str] = []

    if not any(retention_clause(clause) for clause in regression_clauses):
        errors.append("does not explicitly retain the known regression test/case")

    prior_regression = False
    for clause in clauses:
        names_regression = bool(re.search(REGRESSION, clause))
        deletes = bool(re.search(rf"\b{DELETE}\b", clause))
        deletion_negated = bool(
            re.search(rf"(?:do not|don.?t|must not|should not|never)\s+{DELETE}\b", clause)
        )
        anaphoric = bool(
            re.search(rf"\b{DELETE}\s+(?:it|this|that|the)(?:\s+(?:case|test|row|regression))?\b", clause)
        )
        if deletes and not deletion_negated and (names_regression or (prior_regression and anaphoric)):
            errors.append("affirmatively deletes/removes the known regression test")
            break
        prior_regression = names_regression

    if not re.search(
        r"pairwise.{0,100}(?:not|isn.?t|does not|cannot).{0,50}(?:cover|replace|protect|guarantee|subsume|prove|sufficient).{0,70}(?:regression|four[- ]way|4[- ]way|four[- ]factor|high[- ]order|repaired fault|remove|failure)|pairwise.{0,80}(?:not a correctness proof)",
        text,
        re.DOTALL,
    ):
        errors.append("does not explain that pairwise cannot cover/replace this repaired high-order fault")

    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
