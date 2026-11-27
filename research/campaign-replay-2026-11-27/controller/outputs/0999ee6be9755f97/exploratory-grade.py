"""Supplemental per-case grading of the same saved bytes through both submitted manifests."""
import argparse
from difflib import unified_diff
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


HERE = Path(__file__).resolve().parent
PUBLIC = HERE.parent / "participant"
sys.path.insert(0, str(PUBLIC / "support/skill-eval-harness"))
import skill_benchmark


def grade(case, text, manifest, variant, out):
    saved = out / "output.md"
    saved.write_text(text)
    result, deferred = skill_benchmark.grade_case_variant(case, variant, text, saved, {}, run_base=out,
                                                          manifest_dir=manifest.parent, allow_scripts=False)
    return {"passed": result["objective_passed"], "total": result["objective_total"],
            "rate": result["objective_pass_rate"], "criticalVeto": result["vetoed"], "deferred": len(deferred),
            "assertions": [{k: a.get(k) for k in ("name", "type", "passed", "evidence")} for a in result["assertions"]]}


def ablation(repo):
    with tempfile.TemporaryDirectory(prefix="ablation-") as tmp:
        base = Path(tmp)
        copy = base / "checkout"
        shutil.copytree(repo, copy)
        # Both ablation sources are disposable working copies. The pinned source
        # arrives on a read-only mount and otherwise transfers its 0444 modes.
        for directory, _, files in os.walk(copy):
            Path(directory).chmod(0o700)
            for name in files:
                p = Path(directory, name)
                if not p.is_symlink():
                    p.chmod(p.stat().st_mode | 0o200)
        hdr = copy / ".all.json"
        cmd = ["node", "scripts/eval/materialize-skill-runner-manifest.ts", "--manifest",
               "skill-evals/shared-benchmark.json", "--repo-root", ".", "--out", str(hdr)]
        built = subprocess.run(cmd, cwd=copy, capture_output=True, text=True)
        result = {"materializerExit": built.returncode}
        if built.returncode:
            return {**result, "error": built.stderr[-750:]}
        scoped = copy / ".subset.json"
        data = json.loads(hdr.read_text())
        data["ablations"] = [a for a in data["ablations"] if a["id"] == "no-editor-source-of-truth"]
        scoped.write_text(json.dumps(data))
        for label, manifest in (("all", hdr), ("editorOnly", scoped)):
            dest = base / label
            proc = subprocess.run([sys.executable, "-B", str(PUBLIC / "support/skill-eval-harness/skill_benchmark.py"),
                                   "materialize-ablations", str(manifest), "--out-dir", str(dest)],
                                  cwd=copy, text=True, capture_output=True, timeout=30)
            row = {"exit": proc.returncode, "stdout": proc.stdout.replace(str(base), "<temp>"),
                   "stderr": proc.stderr.replace(str(base), "<temp>")}
            if label == "editorOnly" and not proc.returncode:
                before = (copy / "skills/agentic-mermaid-live-editor/SKILL.md").read_text().splitlines()
                for p in dest.rglob("SKILL.md"):
                    after = p.read_text().splitlines()
                    if any("name: agentic-mermaid-live-editor-development" in line for line in after):
                        diff = list(unified_diff(before, after, n=0))
                        row["removedSkillLines"] = [l[1:] for l in diff if l.startswith("-") and not l.startswith("---")]
                        row["addedSkillLines"] = [l[1:] for l in diff if l.startswith("+") and not l.startswith("+++")]
            result[label] = row
        return result


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, type=Path)
    args = ap.parse_args()
    packet = json.loads((HERE / "editor-controls.json").read_text())
    result = {"classification": "exploratory, outside the predeclared prose metric",
              "runtime": "Original pinned grade_case_variant with schema-validity gates and both variant labels.",
              "inputSHA256": sha256((HERE / "editor-controls.json").read_bytes()).hexdigest(), "results": {}}
    for label, repo in (("original", PUBLIC / "repo"), ("candidate", args.repo)):
        manifest = repo / "skill-evals/shared-benchmark.json"
        m = json.loads(manifest.read_text())
        cases = {c["id"]: c for c in m["cases"]}
        row = {"manifestSHA256": sha256(manifest.read_bytes()).hexdigest(), "controls": [], "ablation": ablation(repo)}
        with tempfile.TemporaryDirectory(prefix="editor-grade-") as scratch:
            for entry in packet["inputs"]:
                cid = entry["case"]
                record = {k: entry[k] for k in ("cohort", "case", "id", "expected", "kind")}
                record["answerSHA256"] = sha256(entry["answer"].encode()).hexdigest()
                record["variants"] = {v: grade(cases[cid], entry["answer"], manifest, v, Path(scratch))
                                      for v in ("with_skill", "without_skill")}
                row["controls"].append(record)
        result["results"][label] = row
    print(json.dumps(result, indent=2))
