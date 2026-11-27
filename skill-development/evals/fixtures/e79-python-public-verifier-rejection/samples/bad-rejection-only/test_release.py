import json

from release_verifier import digest_matches, verify_release

PUBLISHED = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_digest_accepts_original():
    assert digest_matches(b"abc", PUBLISHED)


def test_pipeline_rejects_damaged_file(tmp_path):
    (tmp_path / "artifact.bin").write_bytes(b"abd")
    (tmp_path / "manifest.json").write_text(json.dumps({"sha256": PUBLISHED}))
    assert not verify_release(tmp_path)
