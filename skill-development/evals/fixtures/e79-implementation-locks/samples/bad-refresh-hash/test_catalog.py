import hashlib
import pytest
from catalog import export_items, verify_resource

def test_export():
    expected = b'{"items":[]}'
    assert hashlib.sha256(export_items([]).encode()).digest() == hashlib.sha256(expected).digest()

def test_integrity_accepts_original_and_rejects_corruption():
    abc_sha256 = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert verify_resource(b"abc", abc_sha256) == b"abc"
    with pytest.raises(ValueError):
        verify_resource(b"abcd", abc_sha256)
