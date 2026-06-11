import random
import pytest
from kvstore import KvStore, save, load

def build_store(rng, n=60):
    store = KvStore()
    for i in range(n):
        kind = rng.randrange(3)
        ttl = rng.choice([None, rng.randrange(1, 9999)])
        if kind == 0:
            store.set(f"s{i}", f"v{rng.randrange(10**6)}", ttl=ttl)
        elif kind == 1:
            store.set(f"l{i}", [str(rng.randrange(100)) for _ in range(rng.randrange(5))], ttl=ttl)
        else:
            store.set(f"x{i}", {str(rng.randrange(100)) for _ in range(rng.randrange(5))}, ttl=ttl)
    store.set("empty-list", [], ttl=None)
    store.set("empty-set", set(), ttl=None)
    return store

def canonical(store):
    # Sort everything unordered: item order AND set contents.
    out = []
    for key, value, ttl in store.items():
        if isinstance(value, set):
            value = ("set", tuple(sorted(value)))
        elif isinstance(value, list):
            value = ("list", tuple(value))
        else:
            value = ("str", value)
        out.append((key, value, ttl))
    return sorted(out)

@pytest.mark.parametrize("fmt", ["json", "binary"])
def test_save_load_roundtrip_identity(tmp_path, fmt):
    store = build_store(random.Random(1234))
    before = canonical(store)
    save(store, tmp_path / "db", format=fmt)
    reloaded = load(tmp_path / "db", format=fmt)
    assert canonical(reloaded) == before
