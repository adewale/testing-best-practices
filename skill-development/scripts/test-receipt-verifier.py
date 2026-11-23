#!/usr/bin/env python3
"""Exercise receipt verification against evolving code and corrupted evidence."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERIFIER = Path("skill-development/scripts/verify-issues20-21-receipt.py")
RECEIPT = Path("skill-development/evals/attestations/issues-20-21-historical-receipt.json")
OLD_SKILL = Path("skill-development/github-skill-origin-main/testing-best-practices")


class ReceiptVerifierTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.receipt_bytes = (ROOT / RECEIPT).read_bytes()
        receipt = json.loads(self.receipt_bytes)
        self.scripts = list(receipt["current_harness_compatibility"]["current_reproduction_script_sha256"])
        for relative in [VERIFIER, RECEIPT, Path("evals/shared-benchmark.json")]:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        # The receipt names historical paths; fixture setup must not require
        # those scripts to still exist in today's checkout.
        for relative in self.scripts:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("# Synthetic current script, independent of the historical fingerprint.\n")
        shutil.copytree(ROOT / OLD_SKILL, self.root / OLD_SKILL)

    def verify(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(self.root / VERIFIER)],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_original_receipt_passes(self) -> None:
        result = self.verify()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_comment_only_script_edits_are_informational(self) -> None:
        for relative in self.scripts:
            with (self.root / relative).open("a") as script:
                script.write("\n# Comment-only edit; executable behavior is unchanged.\n")
        result = self.verify()
        self.assertEqual(result.returncode, 0, result.stderr)
        for relative in self.scripts:
            self.assertIn(relative, result.stdout)
        self.assertEqual((self.root / RECEIPT).read_bytes(), self.receipt_bytes)

    def test_removed_live_script_is_informational(self) -> None:
        (self.root / self.scripts[0]).unlink()
        result = self.verify()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(self.scripts[0], result.stdout)
        self.assertEqual((self.root / RECEIPT).read_bytes(), self.receipt_bytes)

    def test_changed_historical_artifact_still_fails(self) -> None:
        with (self.root / OLD_SKILL / "SKILL.md").open("a") as archived:
            archived.write("\nAltered historical evidence.\n")
        result = self.verify()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("pinned old skill tree", result.stderr)

    def test_inconsistent_recorded_totals_still_fail(self) -> None:
        receipt = json.loads(self.receipt_bytes)
        receipt["scoring"]["totals"]["with_skill"] += 1
        (self.root / RECEIPT).write_text(json.dumps(receipt))
        result = self.verify()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("recorded objective totals", result.stderr)


if __name__ == "__main__":
    unittest.main()
