"""Replay the controller's late collection with the original and sealed data-only editor objectives."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile


CASES = {"positive": "pos-live-editor-source-of-truth", "adversarial": "adv-reject-editor-html-direct-edit"}
MANIFEST = Path("skill-evals/shared-benchmark.json")


def dump_result(root):
    sys.path.insert(0, str(root / "support"))
    from grade_text import score

    receipt_file = root / "submitted-artifacts/editor-controls-collection.json"
    receipt = json.loads(receipt_file.read_bytes())
    answers = root / "submitted-artifacts/editor-controls"
    specs = {r["path"]: r for r in receipt["files"]}
    assert len(specs) == len(receipt["files"]) == 30
    assert set(specs) == {f.relative_to(answers).as_posix() for f in answers.rglob("*") if f.is_file()}
    manifests = {s: root / s / MANIFEST for s in ("original", "candidate")}
    cases = {s: {row["id"]: row for row in json.loads(m.read_bytes())["cases"]} for s, m in manifests.items()}
    rows = []
    for name, meta in sorted(specs.items()):
        group = Path(name).parts[0]
        cid = CASES[group]
        raw = (answers / name).read_bytes()
        assert len(raw) == meta["bytes"] and sha256(raw).hexdigest() == meta["sha256"]
        text = raw.decode("utf-8")
        try:
            parsed = json.loads(text)
            answer_format = "JSON object" if isinstance(parsed, dict) else "JSON value"
        except json.JSONDecodeError:
            answer_format = "unstructured text"
        row = {"answer": name, "case": cid, "sha256": meta["sha256"], "bytes": len(raw), "format": answer_format}
        for side, manifest in manifests.items():
            case = cases[side][cid]
            assert {a["type"] for a in case["assertions"]} <= {"contains", "contains_all", "regex", "structured_output", "json_field_equals"}
            grade = score(case, text, manifest, allow_scripts=False)
            row[side] = {"passed": grade["passed"], "total": grade["total"], "deferred": grade["deferred"],
                         "assertions": [{"name": a["name"], "passed": a["passed"], "evidence": a["evidence"]} for a in grade["assertions"]]}
        rows.append(row)
    result = {"kind": "Late replay of subject-supplied saved answers. Separate from the frozen matrix and independent exploratory probes.",
              "collectionUTC": receipt["collected_utc"], "collectionSHA256": sha256(receipt_file.read_bytes()).hexdigest(),
              "caseCounts": dict(Counter(Path(r["answer"]).parts[0] for r in rows)),
              "bytesVerified": sum(r["bytes"] for r in rows), "grader": "grade_text.score / grade_case_variant v0.6.0",
              "variant": "with_skill", "allowScripts": False, "python": sys.version.split()[0], "rows": rows}
    print(json.dumps(result, indent=2))


def run_on_host():
    here = Path(__file__).resolve().parent
    campaign = here.parents[2]
    prep = campaign / "preparation/agentic-mermaid"
    sealed = campaign / "controller/candidate-snapshots" / here.name
    spec = json.loads((here / "candidate-snapshot.json").read_bytes())["files"]
    frozen = json.loads((prep / "operator-runtime/runtime-lock.json").read_bytes())["sha256ByRelativePath"]
    pin = json.loads((prep / "operator-runtime/image-pin.json").read_bytes())["imageId"]
    stage_tree = runpy.run_path(str(prep / "run-isolated.py"))["stage_tree"]
    with tempfile.TemporaryDirectory(prefix="mermaid-submitted-answers-") as temp:
        stage = Path(temp)
        stage_tree(here / "submitted-artifacts", stage / "submitted-artifacts")
        stage_tree(prep / "participant/support", stage / "support")
        for f in (stage / "support").rglob("*"):
            if f.is_file():
                assert sha256(f.read_bytes()).hexdigest() == frozen["participant/" + f.relative_to(stage).as_posix()]
        orig = prep / "participant/repo" / MANIFEST
        for side, source, digest in (("original", orig, frozen["participant/repo/" + str(MANIFEST)]),
                                     ("candidate", sealed / MANIFEST, spec[str(MANIFEST)])):
            data = source.read_bytes()
            assert sha256(data).hexdigest() == digest
            out = stage / side / MANIFEST
            out.parent.mkdir(parents=True)
            out.write_bytes(data)
            out.chmod(0o444)
        script = stage / "replay.py"
        shutil.copyfile(__file__, script)
        script.chmod(0o444)
        for f in (stage, *(p for p in stage.rglob("*") if p.is_dir())):
            f.chmod(0o755)
        cmd = ["docker", "--host=unix:///var/run/docker.sock", "run", "--rm", "--pull=never", "--network=none",
               "--read-only", "--user=65534:65534", "--cap-drop=ALL", "--security-opt=no-new-privileges",
               "--cpus=1", "--memory=512m", "--memory-swap=512m", "--pids-limit=64", "--log-driver=none",
               "--tmpfs=/tmp:rw,nosuid,nodev,size=67108864,mode=1777", "--mount", f"type=bind,src={stage},dst=/probe,readonly",
               "--entrypoint=/usr/bin/env", pin, "-i", "PATH=/usr/local/bin:/usr/bin:/bin", "HOME=/tmp", "TMPDIR=/tmp",
               "LC_ALL=C.UTF-8", "/usr/bin/python3", "-I", "-B", "/probe/replay.py", "--inside"]
        subprocess.run(cmd, check=True, timeout=240)


if __name__ == "__main__":
    if sys.argv[1:] == ["--inside"]:
        dump_result(Path("/probe"))
    else:
        run_on_host()
