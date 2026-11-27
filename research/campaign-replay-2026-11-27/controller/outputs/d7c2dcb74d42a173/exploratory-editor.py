"""Replay new example plans and the submitted ablation through the frozen harness."""
import copy
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


def reorder(value):
    if isinstance(value, dict):
        return {k: reorder(v) for k, v in reversed(list(value.items()))}
    return value


def plans(cid):
    standalone = {"path": "editor.html", "builder": "scripts/site/editor.ts", "action": "rebuild", "script": "editor"}
    hosted = {"path": "website/public", "builder": "website/build.ts", "action": "rebuild", "script": "website"}
    base = {"edit": "editor/js/export.js", "standaloneArtifact": standalone, "hostedArtifact": hosted}
    if cid == POS:
        base["formats"] = {"svg": "image", "png": "image", "ascii": "text", "unicode": "text"}
    yield "handler_and_both_builders", "complete", base
    yield "bare_owning_directory", "complete", {**base, "edit": "editor/js"}
    yield "documented_directory_spelling", "directory spelling in shipped skill", {**base, "edit": "editor/js/"}
    yield "hosted_root_trailing_slash", "directory spelling in shipped skill", {**base, "hostedArtifact": {**hosted, "path": "website/public/"}}
    yield "reorder_object_keys", "complete", reorder(base)
    yield "edit_only_assembler", "wrong", {**base, "edit": standalone["builder"]}
    yield "swap_handler_and_standalone_builder", "wrong", {**base, "edit": standalone["builder"],
                                                           "standaloneArtifact": {**standalone, "builder": base["edit"]}}
    yield "hand_edit_standalone_file", "wrong", {**base, "edit": standalone["path"]}
    yield "hand_edit_standalone_action", "wrong", {**base, "standaloneArtifact": {**standalone, "action": "edit"}}
    yield "hand_edit_hosted_action", "wrong", {**base, "hostedArtifact": {**hosted, "action": "edit"}}
    yield "negate_rebuild_of_standalone", "wrong", {**base, "standaloneArtifact": {**standalone, "action": "do not rebuild"}}
    yield "swap_build_scripts", "wrong", {**base, "standaloneArtifact": {**standalone, "script": "website"},
                                           "hostedArtifact": {**hosted, "script": "editor"}}
    yield "omit_standalone_assembler", "correct owner and actions, missing requested builder", {
        **base, "standaloneArtifact": {k: v for k, v in standalone.items() if k != "builder"}}
    yield "equivalent_internal_dot", "correct owner, spelled differently", {**base, "edit": "editor/js/./export.js"}
    yield "leading_dot", "correct owner, leading ./ explicitly excluded by prompt", {**base, "edit": "./editor/js/export.js"}
    yield "true_extra_assembler_note", "complete plan with extra field", {
        **base, "context": "scripts/site/editor.ts assembles editor.html."}
    if cid == POS:
        yield "omit_formats", "wrong", {k: v for k, v in base.items() if k != "formats"}
        yield "swap_image_and_text_formats", "wrong", {
            **base, "formats": {k: ("text" if v == "image" else "image") for k, v in base["formats"].items()}}


def grade_plans(root):
    sys.path.insert(0, str(root / "support"))
    from grade_text import score

    sides = ("original", "candidate")
    manifests = {name: root / name / MANIFEST for name in sides}
    cases = {name: {c["id"]: c for c in json.loads(manifests[name].read_text())["cases"]} for name in sides}
    results = []
    for cid in (POS, ADV):
        for name in sides:
            allowed = {"contains", "contains_all", "regex", "structured_output", "json_field_equals"}
            assert all(a["type"] in allowed for a in cases[name][cid]["assertions"])
        for label, meaning, plan in plans(cid):
            text = json.dumps(plan)
            record = {"case": cid, "example": label, "meaning": meaning, "plan": plan}
            for name in sides:
                grade = score(cases[name][cid], text, manifests[name], allow_scripts=False)
                record[name] = {"passed": grade["passed"], "total": grade["total"], "deferred": grade["deferred"],
                                "failures": {a["name"]: a["evidence"] for a in grade["assertions"] if not a["passed"]}}
            results.append(record)
    return results


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


def inside():
    root = Path("/probe")
    with tempfile.TemporaryDirectory() as temp:
        result = {"status": "Post-freeze independent examples outside the primary matrix. Neither the subject's saved inputs nor live runs.",
                  "python": sys.version.split()[0], "grader": "grade_text.score / grade_case_variant v0.6.0, output.md, allow_scripts=False",
                  "plans": grade_plans(root),
                  "ablationMethod": "Full upstream materialize-ablations on the rooted manifest. The editor-only CLI run projects just that one ablation into a temporary runner manifest.",
                  "ablations": {side: run_ablations(root, side, Path(temp)) for side in ("original", "candidate")}}
    print(json.dumps(result, indent=2))


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


if __name__ == "__main__":
    if sys.argv[1:] == ["--inside"]:
        inside()
    else:
        host()
