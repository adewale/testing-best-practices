#!/usr/bin/env python3
"""A missing oracle runtime must not become a successful negative control."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("run-fixture-oracles.py")
spec = importlib.util.spec_from_file_location("fixture_runner", SCRIPT)
assert spec and spec.loader
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class FixtureRunnerTests(unittest.TestCase):
    def run_case(self, bad_code: int, *, unavailable: bool) -> tuple[int, str]:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            for language in sorted(runner.CORE_LANGS):
                fixture = base / language
                fixture.mkdir()
                (fixture / "good").mkdir()
                (fixture / "bad").mkdir()
                (fixture / "oracle.py").write_text(
                    "import pathlib, sys\n"
                    f"sys.exit(0 if pathlib.Path(sys.argv[1]).name == 'good' else {bad_code})\n"
                )
                manifest = {
                    "language": language, "oracle": "oracle.py",
                    "good_sample": "good", "bad_sample": "bad",
                }
                if unavailable:
                    manifest["unavailable_exit_codes"] = [2]
                (fixture / "manifest.json").write_text(json.dumps(manifest))
            original = runner.FIXTURES
            runner.FIXTURES = base
            output = io.StringIO()
            try:
                with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                    status = runner.main()
            finally:
                runner.FIXTURES = original
            return status, output.getvalue()

    def test_actual_bad_rejection_still_passes(self) -> None:
        status, output = self.run_case(1, unavailable=True)
        self.assertEqual(status, 0, output)

    def test_accepted_bad_sample_fails(self) -> None:
        status, output = self.run_case(0, unavailable=True)
        self.assertNotEqual(status, 0, output)

    def test_unavailable_is_not_a_bad_rejection(self) -> None:
        status, output = self.run_case(2, unavailable=True)
        self.assertNotEqual(status, 0, output)
        self.assertIn("runtime unavailable", output)

    def test_legacy_exit_codes_keep_their_declared_meaning(self) -> None:
        status, output = self.run_case(2, unavailable=False)
        self.assertEqual(status, 0, output)


if __name__ == "__main__":
    unittest.main()
