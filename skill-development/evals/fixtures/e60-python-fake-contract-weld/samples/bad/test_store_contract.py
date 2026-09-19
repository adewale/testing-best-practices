# Bad shape: exercises only the fake's happy paths. Never asserts the
# missing-key contract and never runs anything against RealStore, so both
# drift directions ship silently.
from fake_store import FakeStore


def test_set_and_get():
    store = FakeStore()
    store.set("greeting", "hello")
    assert store.get("greeting") == "hello"


def test_overwrite():
    store = FakeStore()
    store.set("color", "red")
    store.set("color", "blue")
    assert store.get("color") == "blue"


def test_delete():
    store = FakeStore()
    store.set("session", "token")
    store.delete("session")
    assert "session" not in store._data
