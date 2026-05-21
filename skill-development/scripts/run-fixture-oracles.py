#!/usr/bin/env python3
"""Run self-tests for eval fixture oracles.

Each fixture oracle is run against its bundled good and bad samples. Good must
pass; bad must fail. This catches toothless eval oracles before we trust them.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "evals" / "fixtures"
CORE_LANGS = {"python", "go", "typescript", "rust"}


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def main() -> int:
    failures: list[str] = []
    seen_langs: set[str] = set()
    manifests = sorted(FIXTURES.glob("*/manifest.json"))
    if not manifests:
        print("no fixture manifests found", file=sys.stderr)
        return 1

    for manifest_path in manifests:
        fixture_dir = manifest_path.parent
        manifest = json.loads(manifest_path.read_text())
        oracle = fixture_dir / manifest["oracle"]
        good = fixture_dir / manifest["good_sample"]
        bad = fixture_dir / manifest["bad_sample"]
        lang = manifest.get("language", "")
        if lang in CORE_LANGS:
            seen_langs.add(lang)
        for path, label, should_pass in [(good, "good", True), (bad, "bad", False)]:
            if not path.exists():
                failures.append(f"{fixture_dir.name}: missing {label} sample {path}")
                continue
            proc = run([sys.executable, str(oracle), str(path)], cwd=fixture_dir)
            ok = proc.returncode == 0
            if ok != should_pass:
                failures.append(
                    f"{fixture_dir.name}: {label} sample expected {'pass' if should_pass else 'fail'} "
                    f"but got rc={proc.returncode}; stdout={proc.stdout!r}; stderr={proc.stderr!r}"
                )
        print(f"{fixture_dir.name}: good/pass + bad/fail oracle self-test checked")

    missing = CORE_LANGS - seen_langs
    if missing:
        failures.append(f"missing core language fixture oracle(s): {sorted(missing)}")

    if failures:
        print("\nFAILED", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(f"\nOK: {len(manifests)} fixture oracles passed self-tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
