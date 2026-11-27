"""Run the post-submission grader with the isolated wrapper and original pinned image."""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


OUT = Path(__file__).resolve().parent
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--case-dir", type=Path, required=True)
    ap.add_argument("--repo", type=Path, required=True)
    args = ap.parse_args()
    case = args.case_dir.resolve()
    with tempfile.TemporaryDirectory(prefix="post-submission-editor-") as tmp:
        stage = Path(tmp)
        (stage / "operator-runtime").symlink_to(case / "operator-runtime", target_is_directory=True)
        (stage / "participant").symlink_to(case / "participant", target_is_directory=True)
        shutil.copyfile(case / "run-isolated.py", stage / "run-isolated.py")
        hidden = stage / "hidden"
        hidden.mkdir()
        for name in ("editor_controls.py", "manifest_control.py", "visual_controls.py", "workflow_controls.py",
                     "visual-preload.mjs", "run-visual-test.mjs", "run-pixel-helper.mjs", "participant-fingerprint.json", "vendor"):
            (hidden / name).symlink_to(case / "hidden" / name, target_is_directory=name == "vendor")
        shutil.copyfile(OUT / "exploratory-grade.py", hidden / "check_case.py")
        shutil.copyfile(OUT / "exploratory-inputs.json", hidden / "editor-controls.json")
        subprocess.run([sys.executable, "-B", str(stage / "run-isolated.py"), "--repo", str(args.repo.resolve()),
                        "--output", str(OUT / "exploratory-results.json")], check=True)
