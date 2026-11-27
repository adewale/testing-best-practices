"""Run a candidate pytest suite on reference implementations and specified faults."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

IMAGE = "tbp-behavioral-oracles:local"
MAX_REPORT = 1024 * 1024
PYTEST_ARGS = ["-q", "-p", "no:cacheprovider", "--strict-markers"]


TestId = tuple[str, str]


@dataclass
class TestRun:
    exit_code: int
    outcomes: dict[TestId, str]
    observed: set[TestId]


class RunnerError(Exception):
    """A test process did not produce usable evidence."""


def trusted_sample(candidate: Path, fixture: Path) -> bool:
    if os.environ.get("TBP_TRUSTED_FIXTURE_SELF_TEST") != "1":
        return False
    manifest = json.loads((fixture / "manifest.json").read_text())
    samples = manifest.get("good_samples", [manifest.get("good_sample")])
    samples += manifest.get("bad_samples", [manifest.get("bad_sample")])
    return candidate in {(fixture / name).resolve() for name in samples if name}


def pytest_report(work: Path, args: list[str], trusted: bool) -> tuple[int, bytes]:
    if trusted:
        report = work.parent / "report.xml"
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", *args, "--junitxml", str(report)],
            cwd=work,
            env={
                "PATH": os.defpath,
                "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
                "PYTHONDONTWRITEBYTECODE": "1",
            },
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=30,
        )
        if not report.is_file() or report.stat().st_size > MAX_REPORT:
            raise RunnerError(
                "pytest produced no usable report for the checked-in sample"
            )
        return proc.returncode, report.read_bytes()

    # Keep candidate-writable files inside the container. Return a bounded XML
    # report and the actual pytest exit status over the Docker process boundary.
    command = (
        'python -m pytest "$@" --junitxml=/tmp/result.xml >/dev/null 2>&1; status=$?; '
        f"if test -f /tmp/result.xml; then head -c {MAX_REPORT + 1} /tmp/result.xml; fi; "
        'exit "$status"'
    )
    name = "tbp-oracle-" + uuid4().hex
    try:
        proc = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "--pull=never",
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
                "--workdir=/work",
                "--mount",
                f"type=bind,src={work},dst=/work,readonly",
                "--env=PYTEST_DISABLE_PLUGIN_AUTOLOAD=1",
                "--env=PYTHONDONTWRITEBYTECODE=1",
                IMAGE,
                "sh",
                "-c",
                command,
                "oracle",
                *args,
            ],
            capture_output=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=10)
        raise
    if len(proc.stdout) > MAX_REPORT:
        raise RunnerError("isolated pytest report exceeded the size limit")
    if not proc.stdout:
        detail = proc.stderr[-500:].decode(errors="replace").strip()
        hint = (
            f"Build {IMAGE} with Dockerfile.behavioral-oracles. "
            if proc.returncode == 125
            else ""
        )
        raise RunnerError(
            f"isolated pytest produced no report (exit {proc.returncode}). {hint}{detail}"
        )
    return proc.returncode, proc.stdout


def run_tests(candidate: Path, modules: dict[str, str], trusted: bool) -> TestRun:
    with tempfile.TemporaryDirectory(prefix="tbp-behavior-") as tmp:
        work = Path(tmp) / "work"
        work.mkdir()
        work.chmod(0o755)
        for source in candidate.rglob("*.py"):
            if source.is_symlink() or not source.is_file():
                raise ValueError(
                    f"candidate Python source must be a regular file: {source.name}"
                )
            relative = source.relative_to(candidate)
            if relative.as_posix() in modules:
                raise ValueError(
                    f"candidate replaces fixture implementation: {relative}"
                )
            target = work / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        for name, contents in modules.items():
            target = work / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(contents)
        for path in work.rglob("*"):
            path.chmod(0o755 if path.is_dir() else 0o644)
        args = list(PYTEST_ARGS)
        if "_tbp_fixture.py" in modules:
            args += ["-p", "_tbp_fixture"]
        code, xml = pytest_report(work, args, trusted)

    report = ET.fromstring(xml)
    if report.tag not in {"testsuite", "testsuites"} or (
        report.tag == "testsuites" and report.find("testsuite") is None
    ):
        raise RunnerError("pytest returned XML without a test suite")
    if code not in {0, 1, 2, 5}:
        raise RunnerError(f"pytest did not complete normally (exit {code})")
    outcomes = {}
    observed = set()
    for case in report.findall(".//testcase"):
        test_id = (case.get("classname", ""), case.get("name", ""))
        if test_id in outcomes:
            raise ValueError(f"duplicate reported test ID: {test_id}")
        outcomes[test_id] = next(
            (
                status
                for status in ("error", "skipped", "failure")
                if case.find(status) is not None
            ),
            "pass",
        )
        if (
            case.find("./properties/property[@name='tbp_observed'][@value='1']")
            is not None
        ):
            observed.add(test_id)
    if code == 2 and "error" not in outcomes.values():
        raise RunnerError("pytest was interrupted without a reported collection error")
    return TestRun(code, outcomes, observed)


def grade(
    fixture: Path,
    baseline: dict[str, str],
    faults: dict[str, dict[str, str]],
    *,
    required_observations: dict[str, str] | None = None,
) -> int:
    candidate = (Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()).resolve()
    try:
        if not candidate.is_dir():
            raise ValueError("candidate directory does not exist")
        trusted = trusted_sample(candidate, fixture)
        original = run_tests(candidate, baseline, trusted)
        if original.exit_code or set(original.outcomes.values()) != {"pass"}:
            raise ValueError(
                f"reference requires passing, non-skipped tests (pytest exit {original.exit_code}): {original.outcomes}"
            )

        for label, changes in faults.items():
            modified = {**baseline, **changes}
            if modified == baseline:
                raise RunnerError(
                    f"fixture fault {label!r} is identical to a correct implementation"
                )
            result = run_tests(candidate, modified, trusted)
            if result.outcomes.keys() != original.outcomes.keys() or set(
                result.outcomes.values()
            ) & {"skipped", "error"}:
                raise ValueError(
                    f"{label}: test collection changed, skipped, or errored"
                )
            failed = [
                test_id
                for test_id, status in result.outcomes.items()
                if status == "failure"
            ]
            if result.exit_code != 1 or not failed:
                raise ValueError(
                    f"{label}: broken behavior survived the candidate tests (pytest exit {result.exit_code})"
                )
            observation = (required_observations or {}).get(label)
            if observation:
                failed = [
                    test_id
                    for test_id in failed
                    if test_id in original.observed and test_id in result.observed
                ]
                if not failed:
                    raise ValueError(
                        f"{label}: no failing test {observation} in both runs"
                    )
            names = ", ".join(f"{module}.{test}" for module, test in failed)
            print(f"{label}: failed tests: {names}")
    except (RunnerError, OSError, subprocess.SubprocessError, ET.ParseError) as exc:
        print(f"grading unavailable: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0
