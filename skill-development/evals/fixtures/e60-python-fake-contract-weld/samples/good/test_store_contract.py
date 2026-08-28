# One contract suite, executed against BOTH implementations. The fake is
# provably equivalent on the behaviors callers rely on, not assumed to be.
import pytest

from fake_store import FakeStore
from store import RealStore


@pytest.fixture(params=["fake", "real"])
def store(request):
    if request.param == "fake":
        return FakeStore()
    return RealStore(":memory:")


def test_get_returns_what_was_set(store):
    store.set("greeting", "hello")
    assert store.get("greeting") == "hello"


def test_get_missing_key_raises_keyerror(store):
    with pytest.raises(KeyError):
        store.get("absent")


def test_set_overwrites_existing_value(store):
    store.set("color", "red")
    store.set("color", "blue")
    assert store.get("color") == "blue"


def test_delete_removes_key(store):
    store.set("session", "token-abc")
    store.delete("session")
    with pytest.raises(KeyError):
        store.get("session")


def test_delete_missing_key_is_noop(store):
    store.set("keep", "kept")
    store.delete("not-there")
    assert store.get("keep") == "kept"
