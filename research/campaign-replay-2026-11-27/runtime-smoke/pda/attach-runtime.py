#!/usr/bin/env python3
"""Attach shared, locked package versions with independent project-local Vite caches."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, nargs="?", default=HERE/"repo", help="fresh PDA repository directory")
    args = parser.parse_args()
    repo = args.source.resolve()
    config = json.loads((HERE/"runtime.json").read_text())
    locked = Path(config["node_modules"]).resolve()
    if not (locked/"vitest/vitest.mjs").is_file():
        raise SystemExit("The prepared Linux x64 package installation is unavailable.")
    lock = repo/"package-lock.json"
    if not lock.is_file() or hashlib.sha256(lock.read_bytes()).hexdigest() != config["package_lock_sha256"]:
        raise SystemExit("Use the supplied repository and its pinned package lock.")
    local = repo/"node_modules"
    if local.is_symlink():
        raise SystemExit("The source needs its own node_modules directory for local caches.")
    local.mkdir(exist_ok=True)
    for package in sorted(locked.iterdir()):
        if package.name.startswith(".") and package.name != ".bin":
            continue
        dest = local/package.name
        if dest.is_symlink() and dest.resolve() == package.resolve():
            continue
        if dest.exists() or dest.is_symlink():
            raise SystemExit(f"unexpected existing package path: {dest}")
        dest.symlink_to(package, target_is_directory=package.is_dir())
    for dirname in (".vite", ".vite-temp"):
        (local/dirname).mkdir(exist_ok=True)
    if not (repo/".git").exists():
        subprocess.run(["git", "init", "--template=", "-q", str(repo)], check=True)
    print(f"Prepared {repo} with locked packages and independent project caches.")


if __name__ == "__main__":
    main()
