#!/usr/bin/env python3
"""Mechanical pass of the merge-label method (EVAL_ABLATION_DESIGN.md, section 3).

For each campaign PR the owner merged, it compares two trees:

- T0: main as it was just before the merge, merged with the head the campaign
  left (`git merge-tree`). This is what merging the campaign's work unchanged
  would have produced.
- TM: the tree of the owner's actual merge commit.

Every difference between T0 and TM is the owner's rework. Changes that reached
main through other PRs are in both trees and cancel out, so squash-merged
siblings and branches the owner rebuilt are handled the same way.

    python3 merge_labels.py <dir-with-clones> > merge_labels_files.jsonl

<dir-with-clones> holds one clone per repository; a blobless clone is enough.
The output has one line per file the campaign PR changed, labelled:

- kept: TM has exactly the campaign's version;
- removed: TM has main's version, so the PR no longer changes the file;
- changed: TM has a third version;
- conflict: merging the campaign head into main conflicts on this file, so the
  owner had to resolve it (checked by hand).

It also has one line per file the owner changed that the campaign had not
touched (owner-added). Grouping files into units, and the hand check of every
`changed` file, are in merge_labels.jsonl.
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def git(repo: Path, *args: str, ok=(0,)) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if r.returncode not in ok:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def blob(repo: Path, tree: str, path: str) -> str | None:
    r = subprocess.run(["git", "-C", str(repo), "rev-parse", "-q", "--verify", f"{tree}:{path}"],
                       capture_output=True, text=True)
    return r.stdout.strip() or None


def gh(path: str, jq: str) -> str:
    return subprocess.run(["gh", "api", path, "--jq", jq], check=True,
                          capture_output=True, text=True).stdout.strip()


def ensure_commit(repo: Path, owner_repo: str, sha: str) -> None:
    if subprocess.run(["git", "-C", str(repo), "cat-file", "-e", f"{sha}^{{commit}}"]).returncode:
        git(repo, "fetch", "-q", "origin", gh(f"repos/{owner_repo}/commits/{sha}", ".sha"))


def main(clones: Path) -> None:
    merges = json.loads((HERE / "owner_merges_2026-10-09.json").read_text())
    for pr in merges["reworked_campaign_prs"]:
        name, num = pr["repo"], pr["pr"]
        repo, owner_repo = clones / name, f"adewale/{name}"
        merge_sha = gh(f"repos/{owner_repo}/pulls/{num}", ".merge_commit_sha")
        camp = pr["campaign_head"]
        ensure_commit(repo, owner_repo, camp)
        ensure_commit(repo, owner_repo, merge_sha)
        base = git(repo, "rev-parse", f"{merge_sha}^1").strip()  # main just before the merge
        tm = git(repo, "rev-parse", f"{merge_sha}^{{tree}}").strip()
        out = git(repo, "merge-tree", "--write-tree", "--name-only", base, camp, ok=(0, 1)).split("\n")
        t0 = out[0].strip()
        rest = out[1:]
        conflicts = set(rest[:rest.index("")] if "" in rest else rest)
        camp_files = {}
        for line in git(repo, "diff", "--no-renames", "--name-status", f"{base}...{camp}").splitlines():
            status, path = line.split("\t", 1)
            camp_files[path] = status
        numstat = {}
        for line in git(repo, "diff", "--no-renames", "--numstat", f"{base}...{camp}").splitlines():
            add, rem, path = line.split("\t", 2)
            numstat[path] = (int(add) if add != "-" else 0, int(rem) if rem != "-" else 0)
        reworked = set(git(repo, "diff", "--no-renames", "--name-only", t0, tm).split("\n")) - {""}
        edit = {}  # lines the owner added and removed per file (T0 -> TM)
        for line in git(repo, "diff", "--no-renames", "--numstat", t0, tm).splitlines():
            add, rem, path = line.split("\t", 2)
            edit[path] = (int(add) if add != "-" else 0, int(rem) if rem != "-" else 0)
        for path, status in sorted(camp_files.items()):
            b_t0, b_tm, b_base = blob(repo, t0, path), blob(repo, tm, path), blob(repo, base, path)
            if path in conflicts:
                outcome = "conflict"
            elif b_tm == b_t0:
                outcome = "kept"
            elif b_tm == b_base:
                outcome = "removed"
            else:
                outcome = "changed"
            print(json.dumps({"repo": name, "merged_pr": num, "path": path, "campaign_status": status,
                              "campaign_lines": numstat.get(path, (0, 0)), "owner_edit_lines": edit.get(path, (0, 0)),
                              "mech_outcome": outcome}))
        for path in sorted(reworked - set(camp_files)):
            print(json.dumps({"repo": name, "merged_pr": num, "path": path, "campaign_status": None,
                              "campaign_lines": (0, 0), "owner_edit_lines": edit.get(path, (0, 0)),
                              "mech_outcome": "owner-added"}))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
