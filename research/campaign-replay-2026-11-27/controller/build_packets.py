#!/usr/bin/env python3
"""Reconstruct subject packets, study receipts and blind judge inputs locally."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
DEFAULT_REPO = STUDY.parent / "testing-best-practices"
CURRENT = "379e0d9b53130cc29da8ef73a6287947c9bc34f6"
OPENCLAW = "9fd0b7de19b70c97a285d5ff4c852d66f952190e"
HISTORICAL = "research/campaign-replay-2026-11-26/"
SEED = "public-test-audit-replay-v2-20261127-1"
ARMS = ("none", "pr41", "candidate", "openclaw")
CASES_B = {
    "B01": ("agentic-mermaid", "f49196e7f5d6d2f0970a4a76fe62644ee5e9d004", 660, 58, 58, "hidden/criteria.md"),
    "B02": ("keyboardia", "aa67598560f8eaf2509a3ad4bc73edee2f8bea8a", 370, 370, 58, "evaluator/hidden-controls.md"),
    "B03": ("pda", "c0a9a85c8f690eb77313b9627e3ea39cadc58968", 155, 56, 56, "evaluator/SCORING.md"),
}
PDA_RUNTIME = ("RUNTIME.md", "runtime.json", "attach-runtime.py")
TBP = "testing-best-practices/"
OC_ENTRY = ".agents/skills/test-audit/SKILL.md"
OC_ORDINARY = (OC_ENTRY, ".agents/skills/test-audit/references/audit.md",
               "docs/help/testing/writing-tests.md", ".agents/skills/openclaw-testing/SKILL.md",
               "docs/help/testing/boundary-scenarios.md", "docs/help/testing/fixtures.md")
EXTRA_REFERENCES = ("references/test-audit-patterns.md", "references/checker-calibration.md")
A_DELIVERY = (
    "Read only this packet. Work independently without other agents. Write the exact final "
    "JSON response to response.md beside this packet and return the same response.\n\n"
)
OLD_PREFIX = (
    "Use only the task and context in this packet. Do not browse other files, "
    "use the network, run proposed checks, or contact other agents.\n\n"
)
B_DELIVERY = """Read work/task.md and complete that assignment in work/repo/. Only use this cell's packet, work directory, supplied guidance and locally provisioned project runtimes. Work independently. Keep all source edits in your disposable copy. The controller starts the 25-minute clock after the workspace and dependencies are ready.

Use local offline commands. Leave network services, deployments, upstream repositories, controller and evaluator materials, other cells, prior audits, credentials, and other agents outside this assignment. The runtime notes in work/ give the applicable native commands. Dependencies are provisioned before launch. The host's installed runtime and provisioned dependencies are for local execution.

Deliver your exact final report in response.md beside this packet and return the same report. Also save an identical report under work/ if the assignment specifies that location. Leave the actual changed files in work/repo/. Include which files you inspected, which selections actually ran and their results, and limits on your claims.
"""


def sha(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def packet_text(path, candidate, key):
    data = path.read_bytes()
    try:
        candidate[key] = data.decode("utf-8")
    except UnicodeDecodeError:
        candidate[key] = data.decode("utf-8", errors="replace")
        candidate[key + "_encoding"] = "unreadable UTF-8 bytes replaced for display"
        candidate[key + "_original_sha256"] = sha(data)


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file() and path.read_bytes() == data:
        return
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as f:
        f.write(data)
        name = f.name
    os.replace(name, path)


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args])


def files(root, *, vendor=None):
    for parent, dirs, names in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in {".git", "__pycache__"}
                         and (d != "node_modules" or Path(parent) / d == vendor))
        for name in sorted(names):
            path = Path(parent) / name
            if name.endswith(".pyc"):
                continue
            if path.is_symlink() or not path.is_file():
                raise ValueError(f"unexpected source entry: {path}")
            yield path.relative_to(root).as_posix(), path


def digest_tree(rows):
    return sha(b"".join(f"{name}\0{rows[name]}\n".encode() for name in sorted(rows)))


def id_for(*parts):
    return sha("\0".join((SEED, *parts)).encode())[:16]


def historical(repo):
    # Read only fixed trusted historical Python literal; no imported historical module executes.
    import ast
    source = git(repo, "show", CURRENT + ":" + HISTORICAL + "prepare_packets.py")
    tree = ast.parse(source)
    matched = [n.value for n in tree.body if isinstance(n, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == "RESPONSE_FORMAT" for t in n.targets)]
    if len(matched) != 1:
        raise ValueError("missing unique historical response format")
    read = lambda name: git(repo, "show", CURRENT + ":" + HISTORICAL + name)
    cases = json.loads(read("cases.json"))
    assert [c["id"] for c in cases] == [f"R{i:02d}" for i in range(1, 10)]
    return cases, ast.literal_eval(matched[0]), read("grading-instructions.md")


def bundle(repo, rev):
    if rev is None:
        return {TBP + k: p.read_bytes() for k, p in files(repo / TBP)}
    names = git(repo, "ls-tree", "-r", "--name-only", "-z", rev, "--", TBP).decode().split("\0")
    return {n: git(repo, "show", rev + ":" + n) for n in names if n}


def treatments(repo, candidate):
    authority = json.loads((STUDY / "openclaw/source-manifest.json").read_bytes())
    assert authority["pin"]["sha"] == OPENCLAW
    upstream = {}
    for row in authority["files"]:
        if row["local_path"].startswith("source/"):
            data = (STUDY / "openclaw" / row["local_path"]).read_bytes()
            assert sha(data) == row["sha256"]
            upstream[row["path"]] = data
    return {"none": {}, "pr41": bundle(repo, CURRENT), "candidate": bundle(repo, candidate),
            "openclaw": upstream}


def paths_a(arm, case):
    if arm == "none":
        return []
    if arm == "openclaw":
        paths = list(OC_ORDINARY)
        if case["id"] in {"R01", "R03", "R06"}:
            paths.append(".agents/skills/test-audit/CAMPAIGN.md")
        return paths
    paths = ["SKILL.md"] + ["references/" + ref for ref in case["references"]] + ["references/test-audit.md"]
    if arm == "candidate":
        paths.extend(EXTRA_REFERENCES)
    return [TBP + path for path in paths]


def copy_checked(src, dest):
    # Never overwrite an existing local edit in a disposable project.
    if dest.exists():
        if dest.is_symlink() or src.read_bytes() != dest.read_bytes():
            raise ValueError(f"existing work copy differs: {dest}")
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)


def public_case(info):
    name, revision, inventory, available, priority, criteria = info
    case_root = STUDY / "preparation" / name
    public = dict(files(case_root / "participant"))
    extra = {}
    if name == "pda":
        extra = {f: STUDY / "runtime-smoke/pda" / f for f in PDA_RUNTIME}
    public_hashes = {k: sha(p.read_bytes()) for k, p in public.items()}
    vendor = case_root / "hidden/vendor/node_modules" if name == "agentic-mermaid" else None
    controls = {k: sha(p.read_bytes()) for k, p in files(case_root, vendor=vendor)
                if not k.startswith("participant/")}
    assert criteria in controls
    extra_hashes = {k: sha(p.read_bytes()) for k, p in extra.items()}
    if name == "agentic-mermaid":
        native = json.loads((case_root / "hidden/participant-fingerprint.json").read_bytes())
        # Its published fingerprint orders pathlib path components. Our inventory
        # uses complete POSIX strings. The two archives contain identical bytes.
        native_order = sorted(public_hashes, key=Path)
        native_digest = sha(b"".join(f"{k}\0{public_hashes[k]}\n".encode() for k in native_order))
        assert public_hashes == native["files"] and native_digest == native["sha256"]
    elif name == "keyboardia":
        import tarfile
        native = json.loads((case_root / "freeze-manifest.json").read_bytes())
        assert sha((case_root / native["archive"]).read_bytes()) == native["archive_sha256"]
        assert len(public) == native["subject_files"]
        with tarfile.open(case_root / native["archive"], "r:gz") as archive:
            members = {m.name.removeprefix("participant/"): m for m in archive.getmembers() if m.isfile()}
            assert set(members) == set(public_hashes)
            assert all(sha(archive.extractfile(m).read()) == public_hashes[k] for k, m in members.items())
        assert all(controls["evaluator/" + k] == v for k, v in native["evaluator_sha256"].items())
    else:
        native = json.loads((case_root / "evaluator/case-lock.json").read_bytes())
        assert public_hashes == native["participant"]["files"]
        assert extra_hashes == native["runtime_attachments"]["files"]
        assert all(controls[k] == v for k, v in native["evaluator_and_selection"]["files"].items())
    return {
        "repository": "adewale/" + name, "revision": revision, "inventory": inventory,
        "accessible_tests": available, "priority_sample": priority, "criteria": criteria,
        "participant_files": public_hashes, "participant_tree_sha256": digest_tree(public_hashes),
        "supplemental_runtime_files": extra_hashes,
        "control_source_and_evidence_files": controls, "control_source_and_evidence_sha256": digest_tree(controls),
    }, {**public, **extra}


def maps(cases):
    subjects, judges = [], []
    for phase, labels in (("A", [c["id"] for c in cases]), ("B", list(CASES_B))):
        group = []
        for case in labels:
            candidates = []
            for arm in ARMS:
                subject = id_for("subject", phase, case, arm)
                blind = id_for("blind", phase, case, arm)
                group.append({"id": subject, "phase": phase, "case": case, "arm": arm,
                              "blind_id": blind, "packet": f"subjects/{subject}/packet.md"})
                candidates.append({"subject_id": subject, "blind_id": blind})
            random.Random(SEED + "-judge-order-" + case).shuffle(candidates)
            judges.append({"id": id_for("judge", phase, case), "phase": phase,
                           "case": case, "candidates": candidates})
        random.Random(SEED + "-subject-order-" + phase).shuffle(group)
        subjects.extend(group)
    assert len({s["id"] for s in subjects}) == 48
    assert len({s["blind_id"] for s in subjects}) == 48
    assert len({j["id"] for j in judges}) == 12
    return subjects, judges


def prepare(repo, candidate):
    if (HERE / "freeze.json").exists():
        raise SystemExit("A freeze exists. Use verify, judge preparation, or a separate reconstruction directory.")
    if any((STUDY / "subjects").glob("*/response.md")):
        raise SystemExit("Subject responses exist; this run cannot be rebuilt in place.")
    if candidate is not None:
        candidate = git(repo, "rev-parse", "--verify", candidate + "^{commit}").decode().strip()
        if candidate == CURRENT:
            raise ValueError("Candidate equals the current PR head")
    cases, response, grading = historical(repo)
    arms = treatments(repo, candidate)
    enclosures, prep_hashes = {}, {}
    for case, info in CASES_B.items():
        prep_hashes[case], enclosures[case] = public_case(info)
    subjects, judges = maps(cases)
    by_id = {c["id"]: c for c in cases}
    for row in subjects:
        cell = STUDY / "subjects" / row["id"]
        arm = row["arm"]
        if row["phase"] == "A":
            case = by_id[row["case"]]
            references = paths_a(arm, case)
            parts = [f"## Supplied guidance: {name}\n\n" + arms[arm][name].decode() for name in references]
            guide = "\n\n".join(parts) + "\n\n" if parts else ""
            content = (A_DELIVERY + OLD_PREFIX + guide + "## Task\n\n" + case["prompt"]
                       + "\n\n## Response format\n\n" + response + "\n")
        else:
            references = list(sorted(arms[arm]))
            for name in references:
                write(cell / "guidance" / name, arms[arm][name])
            for name, source in enclosures[row["case"]].items():
                copy_checked(source, cell / "work" / name)
            content = B_DELIVERY
            if arm != "none":
                entry = OC_ENTRY if arm == "openclaw" else TBP + "SKILL.md"
                content += "\nYour supplied guidance begins at guidance/" + entry + ". Consult its linked files as applicable.\n"
        write(cell / "packet.md", content.encode())
        row["packet_sha256"] = sha(content.encode())
        row["guidance_paths"] = references
    manifests = {arm: {k: sha(v) for k, v in sorted(f.items())} for arm, f in arms.items()}
    sources = {"arms": manifests, "cases_B": prep_hashes,
               "openclaw_source_manifest_sha256": sha((STUDY / "openclaw/source-manifest.json").read_bytes()),
               "openclaw_target_command_mapping_sha256": sha((STUDY / "openclaw/replay-environment.md").read_bytes())}
    write(HERE / "generation-map.json", json_bytes(subjects))
    write(HERE / "judge-map.json", json_bytes(judges))
    write(HERE / "source-manifest.json", json_bytes(sources))
    write(HERE / "historical-cases.json", json_bytes(cases))
    write(HERE / "grading-a.md", grading)
    write(HERE / "historical-response-format.txt", (response + "\n").encode())
    protocol = {
        "state": "ready for controller freeze" if candidate else "provisional candidate working tree",
        "requested_model": "gpt-6.2-astra", "requested_reasoning_effort": "max", "fresh_no_history": True,
        "concurrency_max": {"A": 6, "B": 3, "B_per_project": 1}, "subjects": {"A": 36, "B": 12}, "judges": {"A": 9, "B": 3},
        "repetitions": 1, "generation_retries": 0, "judge_retries": 0,
        "subject_wall_minutes": {"A": 10, "B": 25}, "token_usage": "unmetered by the backend",
        "seed": SEED, "arms": {"none": None, "pr41": CURRENT, "candidate": candidate, "openclaw": OPENCLAW},
        "phase_A_sources": {"repository": "adewale/testing-best-practices", "ref": CURRENT, "directory": HISTORICAL},
        "phase_B": {k: {n: v for n, v in val.items() if n in {"repository", "revision", "inventory", "accessible_tests", "priority_sample", "criteria"}} for k, val in prep_hashes.items()},
        "rules": "protocol.md", "phase_A_grading": "grading-a.md", "phase_B_grading": "grading-b.md",
        "case_source_and_evaluator_manifest": "source-manifest.json", "generation_map": "generation-map.json",
        "judge_map": "judge-map.json",
    }
    write(HERE / "protocol.json", json_bytes(protocol))
    core = ("protocol.md", "protocol-review.md", "protocol.json", "build_packets.py", "control_run.py", "grading-a.md", "grading-b.md",
            "historical-cases.json", "historical-response-format.txt", "source-manifest.json",
            "generation-map.json", "judge-map.json")
    lock = {"state": protocol["state"], "candidate": candidate,
            "files_sha256": {name: sha((HERE / name).read_bytes()) for name in core}}
    write(HERE / "manifest.json", json_bytes(lock))
    print(f"Prepared {len(subjects)} subject packets and {len(judges)} judge assignments. {protocol['state']}.")


def verify(check_work):
    lock = json.loads((HERE / "manifest.json").read_bytes())
    if (HERE / "freeze.json").is_file():
        frozen = json.loads((HERE / "freeze.json").read_bytes())
        if frozen["manifest_sha256"] != sha((HERE / "manifest.json").read_bytes()):
            raise ValueError("study manifest changed after the freeze")
    for name, expected in lock["files_sha256"].items():
        if sha((HERE / name).read_bytes()) != expected:
            raise ValueError(f"controller hash mismatch: {name}")
    sources = json.loads((HERE / "source-manifest.json").read_bytes())
    subjects = json.loads((HERE / "generation-map.json").read_bytes())
    for key, detail in sources["cases_B"].items():
        regenerated, _ = public_case(CASES_B[key])
        if regenerated != detail:
            raise ValueError(f"case source/control changed: {key}")
    for row in subjects:
        cell = STUDY / "subjects" / row["id"]
        if sha((cell / "packet.md").read_bytes()) != row["packet_sha256"]:
            raise ValueError(f"subject packet mismatch: {row['id']}")
        if row["phase"] != "B":
            continue
        expected = sources["arms"][row["arm"]]
        actual = {n: sha(p.read_bytes()) for n, p in files(cell / "guidance")}
        if actual != expected:
            raise ValueError(f"cell guidance mismatch: {row['id']}")
        if check_work:
            detail = sources["cases_B"][row["case"]]
            for name, digest in (detail["participant_files"] | detail["supplemental_runtime_files"]).items():
                if sha((cell / "work" / name).read_bytes()) != digest:
                    raise ValueError(f"subject project mismatch: {row['id']}/{name}")
    return lock


def judge_packets(phase):
    if not (HERE / "freeze.json").is_file():
        raise ValueError("judges require a frozen study")
    jobs = json.loads((HERE / "judge-map.json").read_bytes())
    cases = {c["id"]: c for c in json.loads((HERE / "historical-cases.json").read_bytes())}
    evidence = HERE / "outputs"
    todo = [j for j in jobs if j["phase"] == phase]
    pending_packets = {}
    for job in todo:
        case = job["case"]
        if phase == "A":
            source = cases[case]
            bundle = {"case": case, "task": source["prompt"],
                      "criteria": [{"criterion": i, "requirement": text} for i, text in enumerate(source["criteria"], 1)]}
        else:
            name, _, _, _, _, rubric = CASES_B[case]
            source = STUDY / "preparation" / name
            bundle = {"case": case, "task": (source / "participant/task.md").read_text(),
                      "case_criteria": (source / rubric).read_text()}
        candidates = []
        for row in job["candidates"]:
            saved = evidence / row["subject_id"]
            receipt = json.loads((saved / "disposition.json").read_bytes())
            state = receipt["state"]
            for filename in ("response.md", "patch.diff"):
                if filename in receipt["files_sha256"]:
                    if sha((saved / filename).read_bytes()) != receipt["files_sha256"][filename]:
                        raise ValueError(f"sealed candidate artifact changed: {row['subject_id']}/{filename}")
            candidate = {"id": row["blind_id"], "disposition": state}
            if (saved / "response.md").is_file():
                candidate["response_source"] = "submitted file"
                packet_text(saved / "response.md", candidate, "raw_response")
            elif (saved / "chat-final.md").is_file():
                candidate["response_source"] = "returned final message; submitted file absent"
                packet_text(saved / "chat-final.md", candidate, "raw_response")
            elif state == "returned":
                raise ValueError(f"missing returned response for {row['subject_id']}")
            if phase == "B":
                candidate["patch"] = ""
                if (saved / "patch.diff").is_file():
                    packet_text(saved / "patch.diff", candidate, "patch")
                candidate["observed_behavior"] = json.loads((saved / "behavior.json").read_bytes())
            candidates.append(candidate)
        bundle["candidates"] = candidates
        instructions = (HERE / ("grading-a.md" if phase == "A" else "grading-b.md")).read_text()
        location = STUDY / "judges" / job["id"]
        delivery = ("Independently grade all four opaque candidates. Read only this packet. "
                    "Save the exact final JSON to verdict.json beside this packet and return it. "
                    "Do not contact other agents, inspect other directories or use the network.\n\n")
        payload = delivery.encode() + (instructions + "\n\n# Evidence\n\n").encode() + json_bytes(bundle)
        if (location / "packet.md").exists() and (location / "packet.md").read_bytes() != payload:
            raise ValueError(f"refusing to alter an existing judge packet for {case}")
        pending_packets[location / "packet.md"] = payload
    for destination, payload in pending_packets.items():
        write(destination, payload)
    print(f"Prepared {len(todo)} blind phase {phase} packets")


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cmds = cli.add_subparsers(dest="cmd", required=True)
    prep = cmds.add_parser("prepare")
    prep.add_argument("--repo", type=Path, default=DEFAULT_REPO)
    prep.add_argument("--candidate", help="A commit from the skill repository. Omit only for provisional generation.")
    check = cmds.add_parser("verify")
    check.add_argument("--work", action="store_true", help="Also require all original subject source bytes")
    cmds.add_parser("freeze", help="Verify every source and record the root-approved manifest before dispatch")
    judge = cmds.add_parser("judges")
    judge.add_argument("--phase", choices=("A", "B"), required=True)
    args = cli.parse_args()
    if args.cmd == "prepare":
        prepare(args.repo.resolve(), args.candidate)
    elif args.cmd == "judges":
        judge_packets(args.phase)
    else:
        lock = verify(args.cmd == "freeze" or args.work)
        if args.cmd == "freeze":
            import datetime
            if not lock["candidate"] or (HERE / "freeze.json").exists():
                raise SystemExit("Freeze requires a committed candidate and no previous checkpoint.")
            write(HERE / "freeze.json", json_bytes({"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  "candidate": lock["candidate"], "manifest_sha256": sha((HERE / "manifest.json").read_bytes())}))
        print(f"{args.cmd} complete: {lock['state']}")


if __name__ == "__main__":
    main()
