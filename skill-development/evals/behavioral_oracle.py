"""Execute fixture tests on trusted implementations and behavioral faults.

Arbitrary candidates run only in an offline Docker container. The host path is
limited to declared fixture self-tests. Containment does not attest that a
deliberately malicious suite cannot inspect and game a reference implementation.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path

IMAGE = "tbp-behavioral-oracles:local"


def trusted_sample(root: Path, fixture: Path) -> bool:
    if os.environ.get("TBP_TRUSTED_FIXTURE_SELF_TEST") != "1":
        return False
    manifest = json.loads((fixture / "manifest.json").read_text())
    names = manifest.get("good_samples", [manifest.get("good_sample")])
    names += manifest.get("bad_samples", [manifest.get("bad_sample")])
    return root in {(fixture / name).resolve() for name in names if name}


def run_tests(root: Path, modules: dict[str, str], *, trusted: bool) -> dict:
    with tempfile.TemporaryDirectory(prefix="tbp-behavior-") as temporary:
        work = Path(temporary) / "work"
        results = Path(temporary) / "results"
        work.mkdir()
        results.mkdir()
        results.chmod(0o777)
        for source in root.rglob("*.py"):
            if source.is_symlink() or not source.resolve().is_relative_to(root):
                raise ValueError("candidate symlinks are not accepted")
            relative = source.relative_to(root)
            if str(relative) in modules:
                raise ValueError(
                    f"candidate replaces trusted implementation: {relative}"
                )
            destination = work / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
        for name, source in modules.items():
            destination = work / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(source)
        work.chmod(0o755)
        for path in work.rglob("*"):
            path.chmod(0o755 if path.is_dir() else 0o644)
        report = results / "result.xml"
        pytest_args = [
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            "--strict-markers",
        ]
        name = "tbp-oracle-" + uuid.uuid4().hex
        if trusted:
            command = [sys.executable, *pytest_args, "--junitxml", str(report)]
            environment = {
                **os.environ,
                "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
                "PYTHONDONTWRITEBYTECODE": "1",
            }
        else:
            command = [
                "docker",
                "run",
                "--rm",
                "--name",
                name,
                "--network=none",
                "--read-only",
                "--cap-drop=ALL",
                "--security-opt=no-new-privileges",
                "--user=65534:65534",
                "--pids-limit=64",
                "--memory=256m",
                "--cpus=1",
                "--tmpfs=/tmp:rw,noexec,nosuid,size=32m",
                "--mount",
                f"type=bind,src={work},dst=/work,readonly",
                "--mount",
                f"type=bind,src={results},dst=/results",
                "--workdir=/work",
                "--env=PYTEST_DISABLE_PLUGIN_AUTOLOAD=1",
                "--env=PYTHONDONTWRITEBYTECODE=1",
                IMAGE,
                "python",
                *pytest_args,
                "--junitxml",
                "/results/result.xml",
            ]
            environment = os.environ.copy()
            Path(temporary).chmod(0o755)
        try:
            process = subprocess.run(
                command,
                cwd=work,
                env=environment,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except subprocess.TimeoutExpired as exc:
            if not trusted:
                subprocess.run(
                    ["docker", "rm", "-f", name], capture_output=True, timeout=10
                )
            raise ValueError("candidate test execution exceeded 30 seconds") from exc
        if not report.exists():
            raise ValueError(
                "test execution produced no result; build the isolated runner first.\n"
                + process.stderr[-1200:]
            )
        cases = ET.parse(report).findall(".//testcase")
        return {
            "code": process.returncode,
            "ids": sorted(
                (case.get("classname", ""), case.get("name", "")) for case in cases
            ),
            "failed": sum(case.find("failure") is not None for case in cases),
            "errors": sum(case.find("error") is not None for case in cases),
            "skipped": sum(case.find("skipped") is not None for case in cases),
            "output": process.stdout[-1500:] + process.stderr[-500:],
        }


def grade(
    root: Path,
    fixture: Path,
    baseline: dict[str, str],
    faults: dict[str, dict[str, str]],
    *,
    equivalents: dict[str, dict[str, str]] | None = None,
) -> int:
    root = root.resolve()
    try:
        trusted = trusted_sample(root, fixture)
        original = run_tests(root, baseline, trusted=trusted)
        if (
            original["code"]
            or not original["ids"]
            or original["skipped"]
            or original["errors"]
        ):
            raise ValueError(
                "candidate must execute non-skipped tests successfully on reference:\n"
                + original["output"]
            )
        for name, modules in (equivalents or {}).items():
            result = run_tests(root, {**baseline, **modules}, trusted=trusted)
            if (
                result["code"]
                or result["ids"] != original["ids"]
                or result["skipped"]
                or result["errors"]
            ):
                raise ValueError(
                    f"{name}: allowed behavior-preserving change rejected:\n"
                    + result["output"]
                )
        for name, modules in faults.items():
            if all(baseline.get(path) == source for path, source in modules.items()):
                raise ValueError(
                    f"{name}: fault did not change the reference implementation"
                )
            result = run_tests(root, {**baseline, **modules}, trusted=trusted)
            if (
                result["ids"] != original["ids"]
                or result["skipped"]
                or result["errors"]
            ):
                raise ValueError(
                    f"{name}: collection changed, skipped, or errored instead of checking behavior"
                )
            if result["code"] != 1 or result["failed"] == 0:
                raise ValueError(
                    f"{name}: broken behavior survived candidate assertions"
                )
    except (OSError, ValueError, subprocess.SubprocessError, ET.ParseError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print("reference passes; every behavioral fault fails an executed assertion")
    return 0
