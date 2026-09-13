#!/usr/bin/env python3
"""Adversarial regression probes for the E64-E68 and E70 prose oracles."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "evals" / "fixtures"
FIXTURE_NAMES = {
    "E64": "e64-hidden-contract-bounded-generator",
    "E65": "e65-hidden-trusted-input-no-fuzz",
    "E66": "e66-execution-reachability",
    "E67": "e67-python-structured-valid-png",
    "E68": "e68-typescript-state-machine-reachability",
    "E70": "e70-hidden-go-fuzz-cadence-restraint",
}


def run_oracle(eval_id: str, assessment: str) -> tuple[bool, str]:
    fixture = FIXTURES / FIXTURE_NAMES[eval_id]
    with tempfile.TemporaryDirectory() as tmp:
        candidate = Path(tmp)
        (candidate / "assessment.md").write_text(assessment)
        proc = subprocess.run(
            [sys.executable, str(fixture / "oracle.py"), str(candidate)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    return proc.returncode == 0, proc.stdout.strip()


def good_sample(eval_id: str) -> str:
    fixture = FIXTURES / FIXTURE_NAMES[eval_id]
    return (fixture / "samples" / "good" / "assessment.md").read_text()


def cases() -> list[tuple[str, str, bool, str]]:
    """Return fresh natural-language positives and adversarial contradictions."""
    return [
        (
            "E64",
            "good-appropriate-as-written",
            True,
            """The non-empty min_size and finite-float exclusions correspond exactly to
the documented contract: empty input has a separate ValueError contract and NaN or
infinity is undefined. The generator constraints are appropriate as written. Add a
focused empty-list ValueError example and strengthen the median oracle with an
independent counting invariant.
""",
        ),
        (
            "E64",
            "bad-include-out-of-contract-values",
            False,
            """The min_size and finite-float exclusions correspond to the documented
non-empty, finite contract. Keep those bounds? No: include empty lists, NaN, and
infinity in this generator anyway. Add a separate empty-list ValueError example and a
stronger independent median counting oracle.
""",
        ),
        (
            "E65",
            "good-no-fuzz-value",
            True,
            """This unexported package helper receives only a typed AuditRecord built from
schema-constrained internal columns and crosses no trust boundary. Table-driven examples
are sufficient and proportional. Fuzzing would add no useful signal here; add cases for
tabs in fields and the zero time value.
""",
        ),
        (
            "E65",
            "bad-double-negative-augment",
            False,
            """The unexported package helper receives a typed internally constructed
AuditRecord and crosses no trust boundary. Table-driven examples are appropriate as a
baseline. Fuzzing is not unnecessary, however: augment the table with a fuzz harness.
""",
        ),
        (
            "E65",
            "good-generic-fuzzing-not-appropriate",
            True,
            good_sample("E65") + "\nFuzzing is not appropriate here.\n",
        ),
        (
            "E66",
            "good-point-property-at-production",
            True,
            """unittest discover does not collect the module-level Hypothesis function.
Switch to pytest and add a checked pytest --collect-only guard. go test ./... runs the
seed corpus as regressions but does not perform active fuzz discovery. Inventory
FuzzDecodeFrame and FuzzParseHeader, then schedule both in a matrix that runs one -fuzz
target per invocation. normalizeCandidate is a test-local duplicate that does not reach
production. Delete it and point the property at production normalizeSlug directly.
""",
        ),
        (
            "E66",
            "bad-reverse-replacement",
            False,
            """unittest discover does not collect the module-level Hypothesis function.
Switch to pytest and add a checked pytest --collect-only guard. go test ./... runs the
seed corpus as regressions but does not perform active fuzz discovery. Inventory
FuzzDecodeFrame and FuzzParseHeader, then schedule both in a matrix that runs one -fuzz
target per invocation. normalizeCandidate is a test-local copied implementation rather
than production coverage. Replace production normalizeSlug with normalizeCandidate.
""",
        ),
        (
            "E66",
            "good-unittest-testcase-alternative",
            True,
            """unittest discover does not collect the module-level Hypothesis function.
Move test_slugify_is_idempotent into a TestCase method and add a guard that verifies the named test appears. Run python -m unittest discover -v as the exact CI command. go test ./... replays the seed corpus as regressions but does not
perform active fuzz discovery. Inventory FuzzDecodeFrame and FuzzParseHeader, then
schedule both in a matrix that runs one -fuzz target per invocation. normalizeCandidate
is a test-local copied implementation rather than production coverage. Delete the copy,
import production normalizeSlug, and call it directly from the property.
""",
        ),
        (
            "E67",
            "good-other-exceptions-fail",
            True,
            """Header-filtered arbitrary bytes are malformed and reject early, never
reaching IHDR, IDAT, scanline, or pixel semantics. Split malformed-input totality from a
valid semantic round-trip property. Construct PNG chunks IHDR, IDAT, IEND, derive every
length and CRC, and generate coherent valid dimensions, bit depth, and color type. Use
Pillow as an independent validator. PNGError is the only expected rejection; any other
exception must fail the property. More max_examples does not solve reachability.
""",
        ),
        (
            "E67",
            "bad-log-and-ignore",
            False,
            """Header-filtered arbitrary bytes are malformed and reject early, never
reaching IHDR, IDAT, scanline, or pixel semantics. Split malformed totality from a valid
semantic round-trip. Build PNG chunks IHDR, IDAT, IEND, calculate lengths and CRCs, and
generate coherent valid dimensions, bit depth, and color type. Validate with Pillow.
Unexpected exceptions should surface in logs and then be ignored by the harness. More
max_examples does not solve reachability.
""",
        ),
        (
            "E68",
            "good-change-check-configure-replay",
            True,
            """fc.commands draws commands independently of check; asyncModelRun evaluates
each check precondition and skips false commands. The coarse check plus early return in
run hides a no-op. Change check to require m.users.has(this.id) and selected-id equality,
then remove the early return. Record accepted effective transition counts; maxCommands
is an upper cap, not executed coverage. Configure fc.assert with seed and path and
fc.commands with replayPath, ensuring every Vitest project, worker, and sandbox receives
the three replay values. No universal run cadence follows from this evidence.
""",
        ),
        (
            "E68",
            "bad-preconditions-prune",
            False,
            good_sample("E68")
            + "\nPreconditions prune the generated command sequence before execution.\n",
        ),
        (
            "E70",
            "good-sensible-no-change",
            True,
            """go test ./... replays the seed corpus as regressions and does not actively
fuzz. The explicit -fuzz matrix performs active discovery for FuzzDecodeFrame and
FuzzParseHeader and runs one target per invocation. The bounded 20s PR smoke and longer
20m scheduled run are a sensible split; no duration or workflow changes are warranted.
Upload each failure artifact and replay command, then commit the minimized input to its
testdata/fuzz corpus.
""",
        ),
        (
            "E70",
            "bad-delete-redundant-schedule",
            False,
            good_sample("E70")
            + "\nThe scheduled fuzz workflow is redundant; delete it.\n",
        ),
        (
            "E70",
            "bad-half-hour-every-pr",
            False,
            good_sample("E70")
            + "\nEvery pull request deserves a half-hour active campaign for both targets.\n",
        ),
        (
            "E70",
            "good-schedule-not-redundant",
            True,
            good_sample("E70")
            + "\nThe scheduled fuzz workflow is not redundant; do not delete it.\n",
        ),
    ]


def main() -> int:
    mismatches: list[str] = []
    for eval_id, name, expected, assessment in cases():
        actual, detail = run_oracle(eval_id, assessment)
        if actual != expected:
            mismatches.append(
                f"{eval_id} {name}: expected pass={expected}, got pass={actual}"
                + (f" ({detail})" if detail else "")
            )

    if mismatches:
        for mismatch in mismatches:
            print(mismatch, file=sys.stderr)
        return 1

    print("OK: 16 PBT/fuzz oracle polarity and semantic-relationship probes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
