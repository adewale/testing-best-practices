"""Replay the selected renewal comparison in copies of the sealed source tree."""

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
EVAL = ROOT / "preparation/pda/evaluator"
SNAP = ROOT / "controller/candidate-snapshots" / OUT.name
PIN = EVAL.parent / "participant/repo"
sys.dont_write_bytecode = True
sys.path.insert(0, str(EVAL))
import controls

TEST = "test/web-push.test.ts"
SENDER = "src/web-push.ts"
AGENT = "src/agent.ts"
SQL = "ON CONFLICT (endpoint) DO UPDATE SET p256dh = excluded.p256dh, auth = excluded.auth"
CHANGES = {
    "stale-auth": (SENDER, SQL, "ON CONFLICT (endpoint) DO UPDATE SET p256dh = excluded.p256dh"),
    "allowed": (SENDER, SQL, "ON CONFLICT (endpoint) DO UPDATE SET (p256dh, auth) = (excluded.p256dh, excluded.auth)"),
    "cleanup": (AGENT, "if (status === 404 || status === 410) this.pushSubscriptions.remove(subscription.endpoint);",
                "if (status === 404) this.pushSubscriptions.remove(subscription.endpoint);"),
}
CASES = ["original-stale-auth", "candidate-stale-auth", "original-clean", "candidate-allowed", "candidate-cleanup"]


def digest(file):
    return hashlib.sha256(file.read_bytes()).hexdigest()


def read(file):
    return json.loads(file.read_text())


def stamp():
    return datetime.now(timezone.utc).isoformat()


def inventory(repo):
    return {p.relative_to(repo).as_posix(): digest(p) for p in repo.rglob("*")
            if p.is_file() and ".git" not in p.relative_to(repo).parts}


def observe(case):
    original, variant = case.split("-", 1)
    sealed = read(OUT / "candidate-snapshot.json")
    for name, sha in read(OUT / "disposition.json")["files_sha256"].items():
        assert digest(OUT / name) == sha
    assert digest(OUT / "patch.diff") == sealed["patch_sha256"]
    pin = {r["path"]: r["sha256"] for r in read(EVAL / "source-manifest.json")["files"]}
    assert inventory(SNAP) == sealed["files"] and inventory(PIN) == pin
    assert {n for n in pin.keys() | sealed["files"].keys() if pin.get(n) != sealed["files"].get(n)} == {TEST}
    with tempfile.TemporaryDirectory(prefix="pda-native-web-push-") as tmp:
        repo = Path(tmp) / "repo"
        shutil.copytree(SNAP, repo, ignore=shutil.ignore_patterns(".git"))
        if original == "original":
            shutil.copyfile(PIN / TEST, repo / TEST)
        assert inventory(repo) == (pin if original == "original" else sealed["files"])
        file, before, after = CHANGES.get(variant, (None, None, None))
        if file:
            source = (repo / file).read_text()
            assert source.count(before) == 1
            (repo / file).write_text(source.replace(before, after))
        plan = [{"config": controls.CONFIG["workers"], "files": [TEST]}]
        if case == "original-clean":
            plan.append({"config": controls.CONFIG["ui"], "files": ["test/ui/workspace.test.tsx"], "name": "notification settings"})
        if case == "candidate-cleanup":
            plan[0]["name"] = "sends one reminder per device using its current keys"
        record = {
            "name": case, "kind": "exploratory after submission", "started_utc": stamp(),
            "source_change": [file, before, after] if file else None, "groups": plan, "image": controls.IMAGE,
            "sha256": {n: digest(repo / n) for n in [SENDER, AGENT, TEST, "test/ui/workspace.test.tsx"]},
        }
        deps = Path(read(EVAL / "local-runtime.json")["node_modules"])
        record["observation"] = controls.execute(repo, deps, plan)
        record["finished_utc"] = stamp()
        return record


if __name__ == "__main__":
    if sys.argv[1:2] == ["--locked"]:
        assert len(sys.argv) == 3 and sys.argv[2] in CASES
        print(json.dumps(observe(sys.argv[2])))
    else:
        for case in sys.argv[1:] or CASES:
            assert case in CASES
            cmd = ["flock", "/tmp/test-audit-v2-docker.lock", sys.executable, "-B", str(Path(__file__).resolve()), "--locked", case]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            item = json.loads(proc.stdout) if not proc.returncode else {"name": case, "runner_exit": proc.returncode, "stderr": proc.stderr, "stdout": proc.stdout}
            with (OUT / "push-runs.ndjson").open("a") as target:
                target.write(json.dumps(item) + "\n")
                target.flush()
                os.fsync(target.fileno())
            groups = item.get("observation", {}).get("results", [])
            print(case, [(g.get("passed"), g.get("failed"), g.get("skipped"), g.get("runnerError")) for g in groups] or item.get("stderr"), flush=True)
