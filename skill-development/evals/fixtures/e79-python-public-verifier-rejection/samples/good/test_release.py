import json

import pytest
from release_verifier import digest_matches, verify_release

PAYLOAD = b"abc"
EXPECTED = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
MANIFEST = json.dumps({"sha256": EXPECTED})


def test_verifier_checks_the_bytes_shipped(tmp_path):
    artifact = tmp_path / "artifact.bin"
    (tmp_path / "manifest.json").write_text(MANIFEST)
    artifact.write_bytes(PAYLOAD)
    assert verify_release(tmp_path)

    artifact.write_bytes(b"abd")
    assert not verify_release(tmp_path)


@pytest.mark.parametrize("changed", [b"", b"ab", b"abc!", b"ABC"])
def test_other_digest_mismatches(changed):
    assert not digest_matches(changed, EXPECTED)
