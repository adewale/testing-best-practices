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


