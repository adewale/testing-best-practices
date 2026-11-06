#!/usr/bin/env python3
"""Check E08/E33 behavior grading, including the arbitrary-candidate boundary."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FIXTURES = Path(__file__).resolve().parents[1] / "evals/fixtures"


def grade(fixture: Path, candidate: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(fixture / "oracle.py"), str(candidate)],
        env={**os.environ, "TBP_TRUSTED_FIXTURE_SELF_TEST": "1"},
        capture_output=True, text=True, timeout=150,
    )


def main() -> int:
    for name in ("e08-deterministic-time", "e33-python-fault-injection"):
        fixture = FIXTURES / name
        manifest = json.loads((fixture / "manifest.json").read_text())
        good = manifest.get("good_samples", [manifest.get("good_sample")])
        bad = manifest.get("bad_samples", [manifest.get("bad_sample")])
        for sample, expected in [(p, True) for p in good] + [(p, False) for p in bad]:
            result = grade(fixture, fixture / sample)
            assert (result.returncode == 0) == expected, f"{name}/{sample}: {result.stdout}\n{result.stderr}"
        # Same tests, outside the exact trusted sample roots: exercise Docker.
        with tempfile.TemporaryDirectory(prefix="tbp-candidate-boundary-") as directory:
            root = Path(directory)
            candidate = root / "candidate"
            shutil.copytree(fixture / good[0], candidate)
            result = grade(fixture, candidate)
            assert result.returncode == 0, result.stdout + result.stderr
            for file in candidate.rglob("*.py"):
                file.unlink()
            (candidate / "test_comments.py").write_text("# fake_clock\n# raise ConnectionError\n# retry\n# assert\n")
            result = grade(fixture, candidate)
            assert result.returncode != 0, "comment-only candidate passed"
            marker = root / "HOST_CODE_EXECUTED"
            (candidate / "test_comments.py").write_text(
                "from pathlib import Path\n"
                "def test_candidate():\n"
                f"    path = Path({str(marker)!r})\n"
                "    path.parent.mkdir(parents=True, exist_ok=True)\n"
                "    path.write_text('candidate execution')\n"
                "    assert True\n"
            )
            result = grade(fixture, candidate)
            assert result.returncode != 0, "unrelated assertions killed no behavioral fault"
            assert not marker.exists(), "ambient self-test flag executed arbitrary code on the host"
        print(f"{name}: reference, faults, vacuity/skip controls and isolated execution passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
