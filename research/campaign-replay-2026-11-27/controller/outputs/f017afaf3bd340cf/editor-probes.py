"""Operator reproduction of saved editor plans, exploratory controls and materialized ablations."""
from collections import Counter
import difflib
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile

POS = "pos-live-editor-source-of-truth"
ADV = "adv-reject-editor-html-direct-edit"
MANIFEST = Path("skill-evals/shared-benchmark.json")
ABLATION = "no-editor-source-of-truth"


def run_ablations(root, side, tmp):
    repo = tmp / side
    shutil.copytree(root / side, repo, copy_function=shutil.copyfile)
    runner = repo / "runner.json"
    proc = subprocess.run(["node", "scripts/eval/materialize-skill-runner-manifest.ts", "--manifest", str(MANIFEST),
                           "--repo-root", ".", "--out", runner.name], cwd=repo, capture_output=True, text=True)
    result = {"materializerExit": proc.returncode}
    if proc.returncode:
        result["materializerDiagnostic"] = proc.stderr.replace(str(tmp), "<tmp>")
        return result
    materialized = json.loads(runner.read_text())
    editor = repo / "editor-only.json"
    editor.write_text(json.dumps({**materialized, "ablations": [a for a in materialized["ablations"] if a["id"] == ABLATION]}))
    cli = str(root / "support/skill-eval-harness/skill_benchmark.py")
    for scope, manifest in (("allDeclared", runner), ("editorOnly", editor)):
        out = tmp / f"{side}-{scope}"
        p = subprocess.run([sys.executable, "-B", cli, "materialize-ablations", manifest.name, "--out-dir", str(out)],
                           cwd=repo, capture_output=True, text=True)
        record = {"exit": p.returncode, "stdout": p.stdout.replace(str(tmp), "<tmp>").strip(),
                  "stderr": p.stderr.replace(str(tmp), "<tmp>").strip()}
        result[scope] = record
        if p.returncode == 0 and scope == "editorOnly":
            old = (repo / "skills/agentic-mermaid-live-editor/SKILL.md").read_text().splitlines()
            files = [f for f in out.rglob("SKILL.md") if "name: agentic-mermaid-live-editor-development" in f.read_text()]
            assert len(files) == 1
            new = files[0].read_text().splitlines()
            diff = list(difflib.ndiff(old, new))
            record["removedLines"] = [s[2:] for s in diff if s.startswith("- ")]
            record["insertedLines"] = [s[2:] for s in diff if s.startswith("+ ")]
    return result


def host():
    here = Path(__file__).resolve().parent
    study = here.parents[2]
    prep = study / "preparation/agentic-mermaid"
    sealed = study / "controller/candidate-snapshots" / here.name
    stage_tree = runpy.run_path(str(prep / "run-isolated.py"))["stage_tree"]
    pin = json.loads((prep / "operator-runtime/image-pin.json").read_text())["imageId"]
    lock = json.loads((prep / "operator-runtime/runtime-lock.json").read_text())["sha256ByRelativePath"]
    spec = json.loads((here / "candidate-snapshot.json").read_text())["files"]
    with tempfile.TemporaryDirectory(prefix="mermaid-editor-probe-") as temp:
        stage = Path(temp)
        stage_tree(prep / "participant/repo", stage / "original")
        stage_tree(sealed, stage / "candidate", ignore={".git", "node_modules", "__pycache__"})
        stage_tree(prep / "participant/support", stage / "support")
        stage_tree(here / "submitted-artifacts", stage / "submitted-artifacts")
        for side in ("original", "candidate", "support"):
            for file in (stage / side).rglob("*"):
                if file.is_file():
                    rel = file.relative_to(stage / side).as_posix()
                    expected = spec[rel] if side == "candidate" else lock[("participant/repo/" if side == "original" else "participant/support/") + rel]
                    assert hashlib.sha256(file.read_bytes()).hexdigest() == expected
        script = stage / "probe.py"
        shutil.copyfile(__file__, script)
        stage.chmod(0o755)
        script.chmod(0o444)
        cmd = ["docker", "--host=unix:///var/run/docker.sock", "run", "--rm", "--pull=never",
               "--network=none", "--read-only", "--user=65534:65534", "--cap-drop=ALL",
               "--security-opt=no-new-privileges", "--cpus=1", "--memory=512m", "--memory-swap=512m",
               "--pids-limit=64", "--log-driver=none", "--tmpfs=/tmp:rw,nosuid,nodev,size=134217728,mode=1777",
               "--mount", f"type=bind,src={stage},dst=/probe,readonly", "--entrypoint=/usr/bin/env",
               pin, "-i", "PATH=/usr/local/bin:/usr/bin:/bin", "HOME=/tmp", "TMPDIR=/tmp", "LC_ALL=C.UTF-8",
               "/usr/bin/python3", "-I", "-B", "/probe/probe.py", "--inside"]
        subprocess.run(cmd, check=True, timeout=240)


def examples(cid):
    standalone = cid == POS
    edit = "editor/js/export.js"
    generator = "scripts/site/editor.ts" if standalone else "website/build.ts"
    generated = "editor.html" if standalone else "website/public/editor/index.html"
    script = "editor" if standalone else "website"
    plan = {"edit": edit, "generator": generator, "generated": generated, "rebuild": script}
    if standalone:
        plan["formats"] = {"svg": "image", "png": "image", "ascii": "text", "unicode": "text"}
    yield "correct_role_assignment", "correct", plan
    yield "reordered_keys_only", "correct", dict(reversed(list(plan.items())))
    yield "mixed_relative_paths", "correct", {**plan, "edit": "./" + edit, "generated": "./" + generated}
    yield "owner_and_generator_swapped", "wrong", {**plan, "edit": generator, "generator": edit}
    yield "edit_generated_file", "wrong", {**plan, "edit": generated}
    yield "negated_rebuild", "wrong", {**plan, "rebuild": "do not rebuild"}
    yield "generated_is_wrong_delivery_target", "wrong", {
        **plan, "generated": "website/public/editor/index.html" if standalone else "editor.html"}
    yield "two_independent_faults", "wrong", {**plan, "edit": generated, "rebuild": "do not rebuild"}
    yield "omit_generator_while_giving_correct_owner_and_script", "missing requested builder", {
        k: v for k, v in plan.items() if k != "generator"}
    yield "directory_instead_of_requested_file", "correct directory, lacks requested file", {
        **plan, "edit": "editor/js/"}
    yield "same_file_with_internal_dot", "same file, alternative spelling", {
        **plan, "edit": "editor/js/./export.js"}
    yield "truthful_context_field", "extra field excluded by prompt", {
        **plan, "context": "scripts/site/editor.ts is the standalone assembler."}
    if standalone:
        yield "missing_unicode", "missing requested format", {
            **plan, "formats": {k: v for k, v in plan["formats"].items() if k != "unicode"}}
        yield "wrong_ascii_role", "wrong", {**plan, "formats": {**plan["formats"], "ascii": "image"}}
    else:
        yield "standalone_plan_used_for_hosted", "wrong", {
            **plan, "generator": "scripts/site/editor.ts", "generated": "editor.html", "rebuild": "editor"}


def compare(root):
    sys.path.insert(0, str(root / "support"))
    from grade_text import score

    manifests = {side: root / side / MANIFEST for side in ("original", "candidate")}
    cases = {s: {c["id"]: c for c in json.loads(path.read_bytes())["cases"]} for s, path in manifests.items()}
    for cid in (POS, ADV):
        for side in cases:
            assert {a["type"] for a in cases[side][cid]["assertions"]} <= {"contains", "contains_all", "regex", "structured_output"}

    def grade(cid, text):
        result = {}
        for side, path in manifests.items():
            g = score(cases[side][cid], text, path, allow_scripts=False)
            result[side] = {"passed": g["passed"], "total": g["total"], "deferred": g["deferred"],
                            "assertions": [{"name": a["name"], "passed": a["passed"], "evidence": a["evidence"]}
                                           for a in g["assertions"]]}
        return result

    folder = root / "submitted-artifacts/controls"
    receipt = root / "submitted-artifacts/controls-collection.json"
    metadata = json.loads(receipt.read_bytes())
    files = {r["path"]: r for r in metadata["files"]}
    assert len(files) == 18 and set(files) == {p.name for p in folder.glob("*.txt")}
    submitted = []
    for name, row in sorted(files.items()):
        data = (folder / name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == row["sha256"] and len(data) == row["bytes"]
        cids = (POS, ADV) if name.endswith("-prose.txt") else ((POS,) if name.startswith("standalone-") else (ADV,))
        for cid in cids:
            submitted.append({"file": name, "case": cid, "sha256": row["sha256"], **grade(cid, data.decode("utf-8"))})
    explorations = []
    for cid in (POS, ADV):
        for label, meaning, plan in examples(cid):
            explorations.append({"case": cid, "example": label, "meaning": meaning, "plan": plan, **grade(cid, json.dumps(plan))})
    return {"grader": "Original and sealed manifests, grade_text.score / grade_case_variant v0.6.0, output.md, allow_scripts=False",
            "collection": {"sha256": hashlib.sha256(receipt.read_bytes()).hexdigest(), "collectedUTC": metadata["collected_utc"],
                           "uniqueFiles": len(files), "totalBytes": sum(f["bytes"] for f in files.values())},
            "subjectSavedAnswers": submitted, "exploratoryIndependentPlans": explorations}


def grade_cli(root, tmp, side):
    chosen = {POS: ["standalone-good.txt", "standalone-edit-html.txt"], ADV: ["hosted-good.txt", "hosted-standalone.txt"]}
    repo = tmp / side
    rooted = json.loads((repo / "runner.json").read_bytes())
    trimmed = {**rooted, "cases": [c for c in rooted["cases"] if c["id"] in chosen]}
    projection = repo / "selected-editor-cases.json"
    projection.write_text(json.dumps(trimmed))
    runs = tmp / (side + "-runs")
    lookup = {}
    for cid, names in chosen.items():
        for number, name in enumerate(names, start=1):
            base = runs / cid / "with_skill" / ("run-" + str(number))
            base.mkdir(parents=True)
            shutil.copyfile(root / "submitted-artifacts/controls" / name, base / "output.md")
            lookup[str(base)] = name
    out = tmp / (side + "-grade.json")
    cli = root / "support/skill-eval-harness/skill_benchmark.py"
    p = subprocess.run([sys.executable, "-B", str(cli), "grade", projection.name, "--runs", str(runs),
                        "--variant", "with_skill", "--out", str(out)], cwd=repo, capture_output=True, text=True)
    result = {"exit": p.returncode, "stdout": p.stdout.replace(str(tmp), "<tmp>").strip(),
              "stderr": p.stderr.replace(str(tmp), "<tmp>").strip()}
    if p.returncode == 0 and out.is_file():
        report = json.loads(out.read_bytes())
        result["judgeTasks"] = report.get("judge_task_count")
        result["rows"] = [{"file": lookup[str(r["run_base"])], "passed": r["objective_passed"], "total": r["objective_total"]}
                          for r in report["results"]]
    return result


def inside():
    root = Path("/probe")
    result = compare(root)
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        result["ablations"] = {s: run_ablations(root, s, tmp) for s in ("original", "candidate")}
        result["cliGrade"] = {s: grade_cli(root, tmp, s) for s in ("original", "candidate")}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    if sys.argv[1:] == ["--inside"]:
        inside()
    else:
        host()
