#!/usr/bin/env python3
"""Run mutation-backed mini-repo self-tests.

For each mini repo, the good implementation must pass and the mutant must fail.
"""
from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MINI = ROOT / "evals" / "mini-repos"


def run(command: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    # Support simple `cd dir && command` and leading VAR=value commands.
    if command.startswith("cd ") and "&&" in command:
        prefix, command = command.split("&&", 1)
        cwd = cwd / prefix.strip().split(maxsplit=1)[1]
        command = command.strip()
    parts = shlex.split(command)
    while parts and "=" in parts[0] and not parts[0].startswith("="):
        key, value = parts.pop(0).split("=", 1)
        env[key] = value
    return subprocess.run(parts, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def main() -> int:
    failures = []
    manifests = sorted(MINI.glob("*/manifest.json"))
    if not manifests:
        print("no mini-repo manifests found", file=sys.stderr)
        return 1
    for manifest_path in manifests:
        repo = manifest_path.parent
        manifest = json.loads(manifest_path.read_text())
        good = run(manifest["good_command"], repo)
        mutant = run(manifest["mutant_command"], repo)
        if good.returncode != 0:
            failures.append(f"{repo.name}: good command failed rc={good.returncode}\n{good.stdout}\n{good.stderr}")
        if mutant.returncode == 0:
            failures.append(f"{repo.name}: mutant command unexpectedly passed\n{mutant.stdout}\n{mutant.stderr}")
        print(f"{repo.name}: good={'pass' if good.returncode == 0 else 'fail'} mutant={'killed' if mutant.returncode != 0 else 'survived'}")
    if failures:
        print("\nFAILED", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(f"\nOK: {len(manifests)} mini-repo mutants killed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
