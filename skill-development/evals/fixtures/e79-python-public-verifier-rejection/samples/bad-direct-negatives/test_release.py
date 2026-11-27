import json

import pytest
from release_verifier import digest_matches, verify_release

PUBLISHED = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_published_release_passes(tmp_path):
    (tmp_path / "artifact.bin").write_bytes(b"abc")
    (tmp_path / "manifest.json").write_text(json.dumps({"sha256": PUBLISHED}))
    assert verify_release(tmp_path)


@pytest.mark.parametrize("tampered", [b"", b"abd", b"abc!", b"ABC"])
def test_checker_rejects_changed_bytes(tampered):
    assert not digest_matches(tampered, PUBLISHED)
