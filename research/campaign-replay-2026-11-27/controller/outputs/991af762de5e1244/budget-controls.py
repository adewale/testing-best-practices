"""Reproduce the exploratory budget checks. Each invocation appends its actual result."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
SNAPSHOT = ROOT / "controller/candidate-snapshots" / OUT.name
EVAL = ROOT / "preparation/pda/evaluator"
PIN = EVAL.parent / "participant/repo"
sys.dont_write_bytecode = True
sys.path.insert(0, str(EVAL))
import controls

BUDGET = "test/budget.test.ts"
COMPACTION = "test/compaction.test.ts"
WITNESS = "test/controller-budget-reachability.test.ts"
RULE = "src/budget.ts"
FROZEN_SHA = "63a7bdbb2f633ec4045468124e15902785ff2caba4516f1b174fd1726c651ed7"
LOCK = "/tmp/test-audit-v2-docker.lock"
NAMES = [
    "original-off-by-one", "candidate-off-by-one", "original-clean",
    "candidate-clean", "candidate-permitted-query", "original-stricter",
    "candidate-stricter", "original-permitted-query", "reachability", "reachability-context",
]
QUERY = "SELECT COUNT(*) AS n FROM model_budget_calls WHERE day = ? AND cost_usd IS NULL"
EDITS = {
    "off-by-one": ("if (Number(unresolved.n) >= 2) return null;", "if (Number(unresolved.n) > 2) return null;"),
    "stricter": ("if (Number(unresolved.n) >= 2) return null;", "if (Number(unresolved.n) >= 1) return null;"),
    "permitted-query": (QUERY, "SELECT COUNT(*) AS n FROM (SELECT 1 FROM model_budget_calls WHERE day = ? AND cost_usd IS NULL LIMIT 2)"),
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stamp():
    return datetime.now(timezone.utc).isoformat()


def load_json(path):
    return json.loads(path.read_text())


def inventory(repo):
    return {
        p.relative_to(repo).as_posix(): digest(p) for p in repo.rglob("*")
        if p.is_file() and ".git" not in p.relative_to(repo).parts
    }


def sources():
    snap = load_json(OUT / "candidate-snapshot.json")
    disposition = load_json(OUT / "disposition.json")
    assert digest(OUT / "pda.json") == FROZEN_SHA
    for path, expected in disposition["files_sha256"].items():
        assert digest(OUT / path) == expected
    assert snap["patch_sha256"] == digest(OUT / "patch.diff")
    assert inventory(SNAPSHOT) == snap["files"]
    pinned = {x["path"]: x["sha256"] for x in load_json(EVAL / "source-manifest.json")["files"]}
    assert inventory(PIN) == pinned
    assert sorted(p for p in set(snap["files"]) | set(pinned) if snap["files"].get(p) != pinned.get(p)) == [BUDGET]
    return pinned, snap["files"]


def run_locked(name):
    pinned, snapshot = sources()
    is_witness = name.startswith("reachability")
    is_original = name.startswith("original-") or is_witness
    variant = "clean" if is_witness else name.partition("-")[2]
    deps = Path(load_json(EVAL / "local-runtime.json")["node_modules"])
    with tempfile.TemporaryDirectory(prefix="pda-budget-native-") as temp:
        repo = Path(temp) / "repo"
        shutil.copytree(SNAPSHOT, repo, ignore=shutil.ignore_patterns(".git"))
        if is_original:
            shutil.copyfile(PIN / BUDGET, repo / BUDGET)
        assert inventory(repo) == (pinned if is_original else snapshot)
        before = digest(repo / RULE)
        if variant in EDITS:
            old, new = EDITS[variant]
            source = (repo / RULE).read_text()
            assert source.count(old) == 1
            (repo / RULE).write_text(source.replace(old, new))
        groups = [{"config": controls.CONFIG["workers"], "files": [BUDGET]}]
        if name == "candidate-clean":
            groups.append({"config": controls.CONFIG["workers"], "files": [COMPACTION]})
        if is_witness:
            shutil.copyfile(OUT / "budget-reachability-witness.ts", repo / WITNESS)
            groups = [{"config": controls.CONFIG["workers"], "files": [WITNESS]}]
            if name == "reachability-context":
                diagnostic = repo / "test/controller-budget-reachability-diagnostic.test.ts"
                source = (repo / WITNESS).read_text()
                old = "      return { dispatched, reason: response.stopReason, refusal, local: ledger.spent(day) };"
                assert source.count(old) == 1
                diagnostic.write_text(source.replace(old, '      if (!dispatched && !refusal) throw new Error("Router failed before a budget refusal: " + response.errorMessage);\n' + old))
                subprocess.run(["git", "apply", str(OUT / "budget-reachability-context.patch")], cwd=repo, check=True)
                groups.append({"config": controls.CONFIG["workers"], "files": [diagnostic.relative_to(repo).as_posix()]})
        evidence = {
            "name": name, "exploratory": True, "started_utc": stamp(),
            "immutable_source": "pinned" if is_original else "candidate",
            "budget_test_sha256": digest(repo / BUDGET), "budget_src_original_sha256": before,
            "budget_src_used_sha256": digest(repo / RULE),
            "single_source_replacement": list(EDITS[variant]) if variant in EDITS else None,
            "controller_witness_sha256": digest(repo / WITNESS) if is_witness else None,
            "groups": groups, "image": controls.IMAGE,
        }
        evidence["observation"] = controls.execute(repo, deps, groups)
        evidence["finished_utc"] = stamp()
        return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--under-flock", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("names", nargs="*", metavar="CONTROL")
    args = parser.parse_args()
    names = args.names or NAMES
    assert all(n in NAMES for n in names)
    if args.under_flock:
        assert len(names) == 1
        print(json.dumps(run_locked(names[0])))
        return
    for name in names:
        command = ["flock", LOCK, sys.executable, "-B", str(Path(__file__).resolve()), "--under-flock", name]
        start = stamp()
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode:
            record = {"name": name, "started_utc": start, "finished_utc": stamp(), "runner_exit": result.returncode,
                      "stderr": result.stderr, "stdout": result.stdout}
        else:
            record = json.loads(result.stdout)
        with (OUT / "budget-runs.ndjson").open("a") as evidence:
            evidence.write(json.dumps(record) + "\n")
            evidence.flush()
            os.fsync(evidence.fileno())
        obs = record.get("observation", {})
        summary = [(r["files"], r.get("passed"), r.get("failed"), r.get("runnerError")) for r in obs.get("results", [])]
        print(name, summary or obs.get("error") or record.get("stderr"), flush=True)


if __name__ == "__main__":
    main()
