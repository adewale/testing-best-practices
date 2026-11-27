import json

import pytest
from release_verifier import verify_release as verify


@pytest.mark.parametrize(("shipped", "accepted"), [(b"", True), (b"x", False)])
def test_release_decision(tmp_path, shipped, accepted):
    published = {"sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}
    (tmp_path / "manifest.json").write_text(json.dumps(published))
    (tmp_path / "artifact.bin").write_bytes(shipped)
    assert verify(tmp_path) is accepted
