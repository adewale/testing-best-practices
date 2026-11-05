import pytest

from fake_store import FakeStore
from store import RealStore


@pytest.fixture(params=["fake", "real"], name="backend")
def store(request):
    if request.param == "fake":
        return FakeStore()
    return RealStore(":memory:")


def test_contract(store):
    store.set("key", "value")
    assert store.get("key") == "value"
    with pytest.raises(KeyError):
        store.get("missing")
