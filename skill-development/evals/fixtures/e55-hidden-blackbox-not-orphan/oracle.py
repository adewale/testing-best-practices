#!/usr/bin/env python3
"""E55 restraint oracle: a black-box test is not an orphan.

The false-green guidance teaches that a test which never imports the module it
names may be disconnected (ORPHAN/REIMPL). The over-application failure is
applying that label to a legitimate black-box test that drives the real system
through its entry point, and then "fixing" it by rewriting or deleting it.

Passing shape: recognise the finding as a false positive / black-box coverage
and do not recommend rewriting-to-import or deletion.

Oracle discipline (see references/false-green.md): match over prose with code
blocks removed, markdown emphasis normalised, and *negated* clauses dropped —
a good answer says "do NOT rewrite these to call price_basket() directly", and
a naive matcher would punish exactly that sentence.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

NEGATION = re.compile(
    r"\b(do not|dont|does not|doesn t|should not|shouldn t|must not|mustn t|"
    r"never|avoid|rather than|instead of|no need to|resist|without)\b"
)


def read(root: Path, ext: str) -> str:
    return "\n".join(p.read_text(errors="ignore") for p in root.rglob(f"*.{ext}"))


def normalise(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.S)  # drop fenced code/commands
    text = re.sub(r"`[^`]*`", " ", text)  # drop inline code spans
    text = re.sub(r"[*_]+", "", text)  # unwrap **bold** / _italic_
    text = text.replace("’", " ").replace("'", " ")
    return text.lower()


def affirmative_clauses(text: str) -> str:
    """Keep only clauses that are not under a negation cue."""
    kept = []
    for sentence in re.split(r"(?<=[.!?;:])\s+|\n", text):
        for clause in re.split(r",\s+(?=but|and)|\s+(?=but\b)", sentence):
            if not NEGATION.search(clause):
                kept.append(clause)
    return " ".join(kept)


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    full = normalise(read(root, "md"))
    claims = affirmative_clauses(full)
    errors: list[str] = []

    # Does the answer recognise the test as legitimate black-box coverage?
    recognises = re.search(
        r"false positive|black.?box|through the (real |application |http )*"
        r"(entry point|route|api)|end.?to.?end|exercis\w+ .{0,40}through|"
        r"integration test|keep them|are fine|not a (real )?problem",
        full,
    )

    # Over-application, asserted affirmatively: rewrite to import, or delete.
    rewrite_to_import = re.search(
        r"rewrite .{0,60}(to )?(import|call)|"
        r"(should|must) import |"
        r"import .{0,30}checkout .{0,30}(directly|instead)|"
        r"call price_basket.{0,20}directly|"
        r"replace .{0,40}with .{0,20}unit test",
        claims,
    )
    deletes = re.search(
        r"delete (the |these |both |two )*(route |api )*tests?|"
        r"remove (the |these |both )*(route |api )*tests?|"
        r"tests? (should|can) be (deleted|removed)",
        claims,
    )

    if rewrite_to_import:
        errors.append(
            "over-applied linkage rule: recommended rewriting the black-box test "
            "to import/call the module directly"
        )
    if deletes:
        errors.append(
            "over-applied linkage rule: recommended deleting a test that does "
            "exercise the named module through the entry point"
        )
    if not recognises:
        errors.append(
            "did not recognise the file as legitimate black-box coverage "
            "(treated the import-based finding as authoritative)"
        )
    if len(full.split()) < 40:
        errors.append("empty assessment")

    for e in errors:
        print(e, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
