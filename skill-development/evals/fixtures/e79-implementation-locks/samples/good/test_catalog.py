import json

import pytest
from catalog import export_items, verify_resource


@pytest.mark.parametrize("items", [
    [],
    [{"id": "one", "label": "Café 雪"}],
    [{"id": "second", "label": "B"}, {"id": "first", "label": "A"}],
])
def test_export_preserves_values_and_list_order(items):
    assert json.loads(export_items(items)) == {"items": items}


def test_integrity_accepts_original_and_rejects_corruption():
    abc_sha256 = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert verify_resource(b"abc", abc_sha256) == b"abc"
    with pytest.raises(ValueError):
        verify_resource(b"abcd", abc_sha256)
