#!/usr/bin/env python3
"""Check acceptance and rejection through the file-backed public verifier."""

import sys
from pathlib import Path

FIXTURE = Path(__file__).resolve().parent
sys.path.insert(0, str(FIXTURE.parents[1]))
from behavioral_oracle import grade

MODULE = "release_verifier.py"
REFERENCE = {MODULE: (FIXTURE / "src" / MODULE).read_text()}
CHECK = 'digest_matches(payload, manifest["sha256"])'
FAULTS = {
    label: {MODULE: REFERENCE[MODULE].replace(f"return {CHECK}", f"{CHECK}\n    return {verdict}")}
    for label, verdict in (
        ("public verifier discards a rejection", True),
        ("public verifier discards an acceptance", False),
    )
}


if __name__ == "__main__":
    raise SystemExit(grade(FIXTURE, REFERENCE, FAULTS))
