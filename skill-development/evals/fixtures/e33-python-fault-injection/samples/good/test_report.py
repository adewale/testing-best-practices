import pytest

from report import ReportSaveError, save_report


class HappyStore:
    """Always succeeds; records what was written."""

    def __init__(self):
        self.writes = []

    def put(self, key, data):
        self.writes.append((key, data))


class AlwaysFailingStore:
    """Models a dependency that is down for the whole call."""

    def __init__(self):
        self.calls = 0

    def put(self, key, data):
        self.calls += 1
        raise ConnectionError("object store unreachable")


class FlakyStore:
    """Fails the first two attempts, then recovers."""

    def __init__(self, fail_times):
        self.calls = 0
        self.fail_times = fail_times

    def put(self, key, data):
        self.calls += 1
        if self.calls <= self.fail_times:
            raise ConnectionError("transient network blip")


def test_happy_path_returns_key():
    store = HappyStore()
    key = save_report({"id": 1, "rows": [1, 2, 3]}, store)
    assert key
    assert len(store.writes) == 1


def test_empty_report_rejected():
    # Argument validation — necessary but not sufficient.
    with pytest.raises(ValueError):
        save_report({}, HappyStore())


def test_transient_failures_are_retried_and_recover():
    store = FlakyStore(fail_times=2)
    key = save_report({"id": 2, "rows": []}, store)
    assert key
    assert store.calls == 3  # two failures retried, third succeeds


def test_exhausted_retries_surface_wrapped_error():
    store = AlwaysFailingStore()
    with pytest.raises(ReportSaveError):
        save_report({"id": 3, "rows": []}, store)
    assert store.calls == 3  # gave up after the retry budget, did not hang
