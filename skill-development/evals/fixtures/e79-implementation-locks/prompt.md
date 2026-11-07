# Repair an AI-written implementation lock

An AI wrote a catalog exporter and tests that pin the SHA-256 of its output.
A whitespace-only serializer refactor fails CI, so another agent proposes
refreshing every hash or deleting all hash checks. Correct the tests instead.

Submit Python pytest tests in named code fences (for example
`test_catalog.py`). Import `export_items` and `verify_resource` from `catalog`.
Do not reimplement or replace those functions.

`export_items(items)` accepts a list of objects with string `id` and `label`
fields and returns JSON `{"items": items}`. Preserve the objects, values and
list order, including an empty list and Unicode. Whitespace and JSON object-key
order are not public contracts. Tests must accept an equivalent serializer.

`verify_resource(payload: bytes, expected_sha256: str)` returns the identical
bytes when their SHA-256 matches, and raises `ValueError` for changed bytes.
This integrity contract must remain tested. Write tests that catch lost labels,
changed list order and an implementation that accepts corrupted resources.
Explain briefly which implementation pin you replaced and which hash remains.
