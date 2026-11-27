#!/usr/bin/env python3
"""Check diagnostic controls and, with --isolated, the built Docker runner."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FIXTURES = Path(__file__).resolve().parents[1] / "evals/fixtures"
SCHEDULER = FIXTURES / "e08-deterministic-time"
REPORT = FIXTURES / "e33-python-fault-injection"
SEARCH = FIXTURES / "e74-python-no-silent-tier-downgrade"


def check(
    fixture: Path, candidate: Path, code: int, evidence: str, *, path: str | None = None
) -> None:
    # A caller can set the flag even for external candidates.
    env = dict(os.environ, TBP_TRUSTED_FIXTURE_SELF_TEST="1")
    if path is not None:
        env["PATH"] = path
    proc = subprocess.run(
        [sys.executable, str(fixture / "oracle.py"), str(candidate)],
        env=env,
        capture_output=True,
        text=True,
        timeout=160,
    )
    output = proc.stdout + proc.stderr
    if proc.returncode != code or evidence not in output:
        raise AssertionError(
            f"{fixture.name}/{candidate.name}: expected rc={code}, {evidence!r}; "
            f"got rc={proc.returncode}\n{output}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--isolated",
        action="store_true",
        help="also exercise the Docker image on external candidates",
    )
    args = parser.parse_args()

    check(SCHEDULER, SCHEDULER / "samples/bad-comments", 1, "pytest exit 5")
    check(SCHEDULER, SCHEDULER / "samples/bad-skipped", 1, "'skipped'")
    check(
        SCHEDULER,
        SCHEDULER / "samples/bad-unrelated",
        1,
        "runs before deadline: broken behavior survived",
    )
    check(
        SCHEDULER,
        SCHEDULER / "samples/bad-blocking-wait",
        1,
        "reference requires passing",
    )
    check(REPORT, REPORT / "samples/bad-import", 1, "pytest exit 2")
    check(
        REPORT,
        REPORT / "samples/bad-exhaustion-only",
        1,
        "loses a successful retry: broken behavior survived",
    )
    check(
        SEARCH,
        SEARCH / "samples/bad-bound-arguments",
        1,
        "SQLite ranks lowest score first: broken behavior survived",
    )
    check(
        SEARCH,
        SEARCH / "samples/bad-unordered",
        1,
        "SQLite ranks lowest score first: broken behavior survived",
    )
    check(
        SEARCH,
        SEARCH / "samples/bad-mocked-order",
        1,
        "no failing test ran the owned search on SQLite",
    )
    print(
        "Checked reference execution, vacuous tests, lost recovery, mock-only ranking and unordered SQLite results."
    )

    with tempfile.TemporaryDirectory(prefix="tbp-boundary-") as tmp:
        root = Path(tmp)
        empty_path = root / "empty-path"
        empty_path.mkdir()
        marker = root / "host-only"
        marker.touch()
        candidate = root / "candidate"
        for fixture, sample, evidence in (
            (SCHEDULER, "good-manual-clock", "test_one_delivery_at_the_deadline"),
            (REPORT, "good-mock-store", "test_attempt_budget_ends_in_a_save_error"),
            (SEARCH, "good-file-database", "test_best_partial_match_is_first"),
        ):
            shutil.copytree(fixture / "samples" / sample, candidate)
            (candidate / "test_isolation.py").write_text(
                "from pathlib import Path\n\n"
                "def test_host_directory_is_outside_runner():\n"
                f"    assert not Path({str(marker)!r}).exists()\n"
            )
            check(fixture, candidate, 2, "grading unavailable", path=str(empty_path))
            if args.isolated:
                check(fixture, candidate, 0, evidence)
            shutil.rmtree(candidate)
        if args.isolated:
            check(
                SEARCH,
                SEARCH / "input",
                0,
                "SQLite ranks lowest score first: failed tests: test_search.test_search_ranks_partial_matches_by_score",
            )
            # The standalone rank fault must still reverse results after a
            # behavior-preserving change to SQL spelling and local variables.
            alternate = root / "evals" / "fixtures" / SEARCH.name
            shutil.copytree(SEARCH, alternate, ignore=shutil.ignore_patterns("samples", "input", "__pycache__"))
            shutil.copyfile(SEARCH.parents[1] / "behavioral_oracle.py", root / "evals" / "behavioral_oracle.py")
            shutil.copyfile(SEARCH / "equivalent/search.py", alternate / "src/search.py")
            check(
                alternate,
                SEARCH / "samples/good-file-database",
                0,
                "SQLite ranks lowest score first: failed tests: test_candidate.test_best_partial_match_is_first",
            )
            print(
                "Docker graded all three copied suites, the original SQLite keeper and an equivalent SQL implementation."
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
