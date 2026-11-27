import json
from hashlib import sha256
from pathlib import Path


def digest_matches(payload: bytes, expected: str) -> bool:
    return sha256(payload).hexdigest() == expected


def verify_release(directory: Path) -> bool:
    manifest = json.loads((directory / "manifest.json").read_bytes())
    payload = (directory / "artifact.bin").read_bytes()
    return digest_matches(payload, manifest["sha256"])
