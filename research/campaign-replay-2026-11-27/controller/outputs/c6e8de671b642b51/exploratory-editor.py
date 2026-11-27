"""Operator-only saved-plan probes. Run from the host through the study Docker lock."""
import copy
import hashlib
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


POSITIVE = "pos-live-editor-source-of-truth"
ADVERSARIAL = "adv-reject-editor-html-direct-edit"


def plans(case_id):
    base = {
        "edit": ["editor/js/export.js"],
        "artifact": {"path": "editor.html", "action": "rebuild"},
        "build": {"standalone": "editor", "hosted": "website"},
    }
    if case_id == POSITIVE:
        base["formats"] = {"svg": "download", "png": "download", "ascii": "copy", "unicode": "copy"}
    yield "owner_and_both_builds", "correct", base
    alternate = copy.deepcopy(base)
    alternate.update(edit=["./editor/js/"], artifact={"path": "./editor.html", "action": "regenerate"},
                     build={"standalone": "bun run editor", "hosted": "bun run website"})
    if case_id == POSITIVE:
        alternate["formats"].update(svg="copy", png="copy")
    yield "source_directory_and_other_valid_actions", "correct", alternate
    yield "assembler_as_only_edit", "wrong", {**base, "edit": ["scripts/site/editor.ts"]}
    yield "includes_hand_edit_of_generated_file", "wrong", {**base, "edit": [*base["edit"], "editor.html"]}
    yield "artifact_action_is_hand_edit", "wrong", {**base, "artifact": {**base["artifact"], "action": "edit"}}
    yield "wrong_standalone_artifact", "wrong", {**base, "artifact": {**base["artifact"], "path": "website/public/index.html"}}
    yield "omit_required_rebuilds", "wrong", {**base, "build": {"standalone": None, "hosted": None}}
    yield "swap_build_owners", "wrong", {**base, "build": {"standalone": "website", "hosted": "editor"}}
    if case_id == POSITIVE:
        yield "omit_formats", "wrong", {k: v for k, v in base.items() if k != "formats"}
        yield "assign_download_to_ascii", "wrong", {**base, "formats": {**base["formats"], "ascii": "download"}}
    yield "equivalent_repo_relative_owner", "same file, alternative spelling", {**base, "edit": ["editor/js/./export.js"]}
    yield "add_true_assembler_context", "correct guidance, additional field", {
        **base, "context": "scripts/site/editor.ts assembles the standalone page."
    }


def run_in_image():
    root = Path("/probe")
    sys.path.insert(0, str(root / "support"))
    from grade_text import score

    manifests = {k: root / k / "skill-evals/shared-benchmark.json" for k in ("original", "candidate")}
    rows = {k: {r["id"]: r for r in json.loads(p.read_text())["cases"]} for k, p in manifests.items()}
    result = {"status": "Exploratory operator-authored examples after freeze; excluded from the frozen prose matrix.",
              "grader": "Frozen grade_text.score / skill_benchmark.grade_case_variant v0.6.0, with_skill, output.md, allow_scripts=False",
              "python": sys.version.split()[0], "judgments": []}
    allowed = {"contains", "contains_all", "regex", "structured_output"}
    for case_id in (POSITIVE, ADVERSARIAL):
        for side in rows:
            assert all(a["type"] in allowed for a in rows[side][case_id]["assertions"])
        for name, intended, plan in plans(case_id):
            answer = json.dumps(plan)
            obs = {"case": case_id, "example": name, "meaning": intended, "plan": plan}
            for k, manifest in manifests.items():
                grade = score(rows[k][case_id], answer, manifest, allow_scripts=False)
                obs[k] = {
                    "passed": grade["passed"], "total": grade["total"], "deferred": grade["deferred"],
                    "decision": "accept" if grade["total"] and grade["passed"] == grade["total"] else "reject",
                    "failures": {a["name"]: a["evidence"] for a in grade["assertions"] if not a["passed"]},
                }
            result["judgments"].append(obs)
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        source = repo / "skill-evals/shared-benchmark.json"
        source.parent.mkdir()
        shutil.copyfile(manifests["candidate"], source)
        out = repo / "fresh.json"
        subprocess.run(["node", str(root / "materialize-skill-runner-manifest.ts"),
                        "--manifest", str(source), "--repo-root", str(repo), "--out", str(out)],
                       check=True, stdout=subprocess.DEVNULL)
        included = json.loads((root / "included-runner.json").read_text())
        fresh = json.loads(out.read_text())
        abs_refs = []
        for entry in fresh["cases"]:
            source_case = next(c for c in included["cases"] if c["id"] == entry["id"])
            for a, c in zip(entry.get("assertions", []), source_case.get("assertions", []), strict=True):
                cmd = a.get("command", [])
                for i, token in enumerate(cmd[:-1]):
                    if token != "--source-file":
                        continue
                    fresh_value = Path(cmd[i + 1])
                    stored_value = Path(c["command"][i + 1])
                    suffix = fresh_value.relative_to(repo)
                    abs_refs.append({"case": entry["id"], "repositoryFile": str(suffix),
                                     "isAbsolute": stored_value.is_absolute(),
                                     "sameRelativeSuffix": stored_value.parts[-len(suffix.parts):] == suffix.parts,
                                     "differsFromFreshCheckout": fresh_value != stored_value})
                    if fresh_value != stored_value and stored_value.parts[-len(suffix.parts):] == suffix.parts:
                        c["command"][i + 1] = str(fresh_value)
        result["includedRunnerCopy"] = {"bytes": (root / "included-runner.json").stat().st_size,
                                        "absoluteSourceArguments": abs_refs,
                                        "matchesFreshMaterializationAfterRebasingThoseArguments": included == fresh}
    print(json.dumps(result, indent=2))


def run_on_host():
    here = Path(__file__).resolve().parent
    campaign = here.parents[2]
    prep = campaign / "preparation/agentic-mermaid"
    candidate = campaign / "controller/candidate-snapshots" / here.name
    image = json.loads((prep / "operator-runtime/image-pin.json").read_text())["imageId"]
    trusted = json.loads((prep / "operator-runtime/runtime-lock.json").read_text())["sha256ByRelativePath"]
    sealed = json.loads((here / "candidate-snapshot.json").read_text())["files"]
    manifest = Path("skill-evals/shared-benchmark.json")
    owner = Path("scripts/eval/materialize-skill-runner-manifest.ts")
    with tempfile.TemporaryDirectory(prefix="editor-grade-readonly-") as tmp:
        stage = Path(tmp)
        original = prep / "participant/repo"
        selected = {
            Path(__file__): stage / "exploratory-editor.py",
            original / manifest: stage / "original" / manifest,
            candidate / manifest: stage / "candidate" / manifest,
            candidate / ".audit-runner-manifest.json": stage / "included-runner.json",
            original / owner: stage / owner.name,
        }
        support = prep / "participant/support"
        for path in itertools.chain([support / "grade_text.py"], sorted((support / "skill-eval-harness").glob("*.py"))):
            selected[path] = stage / "support" / path.relative_to(support)
        for source, dest in selected.items():
            data = source.read_bytes()
            checksum = hashlib.sha256(data).hexdigest()
            if source.is_relative_to(prep):
                assert checksum == trusted[str(source.relative_to(prep))], source.name
            elif source.is_relative_to(candidate):
                assert checksum == sealed[str(source.relative_to(candidate))], source.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            dest.chmod(0o444)
        assert (candidate / owner).read_bytes() == (original / owner).read_bytes()
        for folder in [stage, *(p for p in stage.rglob("*") if p.is_dir())]:
            folder.chmod(0o755)
        cmd = ["docker", "--host=unix:///var/run/docker.sock", "run", "--rm", "--pull=never",
               "--network=none", "--read-only", "--user=65534:65534", "--cap-drop=ALL",
               "--security-opt=no-new-privileges", "--cpus=1", "--memory=512m", "--memory-swap=512m",
               "--pids-limit=64", "--log-driver=none", "--tmpfs=/tmp:rw,nosuid,nodev,size=67108864,mode=1777",
               "--mount", f"type=bind,src={stage},dst=/probe,readonly", "--entrypoint=/usr/bin/env",
               image, "-i", "PATH=/usr/local/bin:/usr/bin:/bin", "HOME=/tmp", "TMPDIR=/tmp",
               "LC_ALL=C.UTF-8", "/usr/bin/python3", "-I", "-B", "/probe/exploratory-editor.py", "--inside"]
        subprocess.run(cmd, check=True, timeout=240)


if __name__ == "__main__":
    if sys.argv[1:] == ["--inside"]:
        run_in_image()
    else:
        run_on_host()
