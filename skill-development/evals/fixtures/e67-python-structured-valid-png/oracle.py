#!/usr/bin/env python3
"""E67 oracle: the strategy must reach valid PNG semantics, not just rejection."""
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

    reachability = has(
        r"(arbitrary|random).{0,100}bytes.{0,220}(malformed|reject|early|semantic|deep)"
        r"|(header|signature).{0,180}(filter|assume).{0,180}(does not|doesn.t|rarely|never).{0,100}"
        r"(ihdr|idat|semantic|scanline|pixel)"
        r"|(parse_ihdr|inflate_idat).{0,160}(0%|unreached|not reached)",
        low,
    )
    if not reachability:
        errors.append("does not diagnose that header-filtered arbitrary bytes miss semantic PNG paths")

    chunk_shape = affirmed(
        r"\b(construct|build|generate|create|emit)\b.{0,180}(chunk|png)", low
    ) and affirmed(
        r"\b(derive|compute|calculate|write|encode)\b.{0,100}(length|size|crc)", low
    )
    required_chunks = all(name in low for name in ("ihdr", "idat", "iend"))
    coherent_fields = affirmed(
        r"\b(generate|choose|constrain|derive|keep)\b.{0,180}"
        r"(dimension|width|height|color type|bit depth).{0,140}"
        r"(coherent|consistent|valid|allowed|contract|matching)"
        r"|\b(generate|choose|constrain|derive|keep)\b.{0,180}"
        r"(coherent|consistent|valid|allowed|contract|matching).{0,140}"
        r"(dimension|width|height|color type|bit depth)",
        low,
    )
    if not (chunk_shape and required_chunks and coherent_fields):
        errors.append("does not specify a structured-valid generator with coherent chunks, CRCs, and IHDR fields")

    separate_tests = affirmed(
        r"\b(separate|split|keep)\b.{0,500}(malformed|arbitrary|totality).{0,500}"
        r"(valid|semantic|round.?trip)",
        low,
    )
    if not separate_tests:
        errors.append("does not separate malformed-input totality from valid-image semantic properties")

    independent = affirmed(
        r"\b(validate|compare|check|decode|use)\b.{0,180}"
        r"(independent (oracle|decoder|validator|check)|reference decoder|pillow|pngcheck)"
        r"|\b(validate|compare|check|decode|use)\b.{0,180}"
        r"(round.?trip).{0,160}(reference|independent)",
        low,
    )
    if not independent:
        errors.append("does not validate generated images or semantics with an independent oracle")

    escape = affirmed_predicate_after(
        r"\bunexpected (?:exceptions?|failures?)\b",
        r"\b(escape|fail|surface|propagate)\b",
        low,
    ) or affirmed_predicate_after(
        r"\b(?:any|all|every)\s+(?:other\s+)?(?:exceptions?|failures?)\b",
        r"\b(?:fail|escape|surface|propagate)\w*\b",
        low,
    ) or affirmed(
        r"\b(?:catch|accept)\b[^.!?\n]{0,80}\bonly\b[^.!?\n]{0,80}"
        r"(?:documented|pngerror)",
        low,
    )
    if not escape:
        errors.append("does not require unexpected exceptions to escape the harness")

    if affirmed(r"\b(catch|swallow)\b.{0,60}(baseexception|exception|all exceptions)", low) or affirmed(
        r"\bexcept\s+(baseexception|exception)\b", low
    ):
        errors.append("recommends swallowing unexpected exceptions")
    if affirmed_predicate_after(
        r"\bunexpected (?:exceptions?|failures?)\b",
        r"\b(mask|hide|suppress|swallow|ignore|discard)\w*\b",
        low,
    ):
        errors.append("recommends masking unexpected exceptions")
    if affirmed_predicate_after(
        r"\b(increase|raise|more)\b.{0,50}(max_examples|examples)",
        r"\b(solve|fix|reach|enough|sufficient)\b",
        low,
    ):
        errors.append("claims more arbitrary examples solve structural reachability")
    if affirmed_predicate_after(
        r"\barbitrary bytes\b",
        r"\b(sufficient|enough|right generator|appropriate generator)\b",
        low,
    ):
        errors.append("treats arbitrary bytes as sufficient for semantic PNG testing")

    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
