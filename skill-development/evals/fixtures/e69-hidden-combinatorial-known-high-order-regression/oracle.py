#!/usr/bin/env python3
from __future__ import annotations
import re, sys
from pathlib import Path


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    text = "\n".join(p.read_text(errors="ignore") for p in root.rglob("*.md")).lower().replace("*", "").replace("`", "")
    text = text.split("acceptance-report", 1)[0]
    errors = []
    clauses = [part.strip() for part in re.split(r"[.;!?\n]+", text) if part.strip()]
    regression_clauses = [c for c in clauses if re.search(r"regression|repaired fault|known.{0,20}(?:case|test|fault)", c)]

    def retention_clause(clause: str) -> bool:
        retains = re.search(r"\b(?:keep|retain)\b|must remain|do not delete|don.?t delete|must not remove|should not remove", clause)
        negates_retention = re.search(r"(?:do not|don.?t|never|not to)\s+(?:keep|retain|preserve)\b", clause)
        return bool(retains and not negates_retention)

    retention = any(retention_clause(clause) for clause in regression_clauses)
    affirmative_delete = False
    for index, clause in enumerate(clauses):
        deletes = re.search(r"\b(?:delete|remove|discard|drop)\b", clause)
        deletion_negated = re.search(r"(?:do not|don.?t|must not|should not|never)\s+(?:delete|remove|discard|drop)\b|reject.{0,20}(?:delet|remov|discard|drop)", clause)
        conditional = re.search(r"only after|provided that|once .{0,40}(?:prove|demonstrat|preserv)|^if\b", clause)
        names_regression = clause in regression_clauses
        anaphoric = bool(re.search(r"\b(?:delete|remove|discard|drop)\s+(?:it|this|that)(?:\s+(?:case|test|row))?\b", clause))
        follows_regression = index > 0 and clauses[index - 1] in regression_clauses
        if deletes and not deletion_negated and not conditional and (names_regression or (anaphoric and follows_regression)):
            affirmative_delete = True
    if not retention:
        errors.append("does not explicitly retain the known regression")
    if affirmative_delete:
        errors.append("affirmatively deletes/removes the known regression")
    if not re.search(r"pairwise.{0,100}(?:not|isn.?t|does not|cannot).{0,50}(?:cover|replace|guarantee|subsume|prove|sufficient).{0,70}(?:regression|four[- ]way|4[- ]way|four[- ]factor|high[- ]order|repaired fault|remove|failure)|pairwise.{0,80}(?:not a correctness proof)", text, re.S):
        errors.append("does not explain that pairwise cannot cover/replace this repaired high-order fault")
    for error in errors: print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
