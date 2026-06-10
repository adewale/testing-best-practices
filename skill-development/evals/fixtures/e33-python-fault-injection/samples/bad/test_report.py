import pytest

from report import save_report


class FakeStore:
    """Stub that always succeeds — the failure path is never exercised."""

    def __init__(self):
        self.writes = []

    def put(self, key, data):
        self.writes.append((key, data))


def test_happy_path_returns_key():
    store = FakeStore()
    key = save_report({"id": 1, "rows": [1, 2, 3]}, store)
    assert key
    assert len(store.writes) == 1


def test_another_happy_report():
    store = FakeStore()
    key = save_report({"id": 2, "rows": ["a", "b"]}, store)
    assert key


def test_empty_report_rejected():
    # Only argument validation — no downstream failure is ever injected,
    # so retries / wrapped-error handling go completely untested.
    with pytest.raises(ValueError):
        save_report({}, FakeStore())
