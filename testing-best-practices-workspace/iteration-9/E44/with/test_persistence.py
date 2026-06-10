"""
Tests for kvstore persistence (save/load).

Strategy: whole-state roundtrip identity checks using seeded RNG-generated
stores that cover every supported value type and edge case. State is
canonicalized before comparison so that unordered structures (sets, dict
iteration) never produce false failures or false passes.
"""

import random
import string
import pytest
from kvstore import KvStore, save, load


# ---------------------------------------------------------------------------
# Canonical dump helpers
# ---------------------------------------------------------------------------

def _canonical_value(v):
    """Return a deterministically ordered representation of a value."""
    if isinstance(v, set):
        return ("set", sorted(v))
    if isinstance(v, list):
        return ("list", v)
    if isinstance(v, str):
        return ("str", v)
    raise TypeError(f"Unsupported value type: {type(v)}")


def canonical_dump(store):
    """
    Return a stable, fully-ordered snapshot of the entire store state.

    Covers keys, values (all types), and TTLs so that bugs in any of those
    fields are visible in the diff rather than silently ignored.
    """
    rows = []
    for key, value, ttl in store.items():
        rows.append((key, _canonical_value(value), ttl))
    # Sort by key so map-iteration order never matters.
    rows.sort(key=lambda r: r[0])
    return rows


# ---------------------------------------------------------------------------
# Store builder
# ---------------------------------------------------------------------------

_CHARSET = string.ascii_letters + string.digits + "_-"
_UNICODE_EXTRAS = ["café", "日本語", "emoji🎉", "ñoño", "Ünïcödé"]


def _rand_str(rng, min_len=1, max_len=12):
    length = rng.randint(min_len, max_len)
    return "".join(rng.choice(_CHARSET) for _ in range(length))


def _rand_value(rng):
    """Return a random str, list[str], or set[str] value."""
    kind = rng.choice(["str", "list", "set"])
    if kind == "str":
        return rng.choice(_UNICODE_EXTRAS + [_rand_str(rng)])
    if kind == "list":
        size = rng.randint(0, 6)
        return [_rand_str(rng) for _ in range(size)]
    # set
    size = rng.randint(0, 6)
    return {_rand_str(rng) for _ in range(size)}


def build_seeded_store(rng, keys=200):
    """
    Build a KvStore with rich, deterministic contents:
      - string, list, and set values
      - some keys with TTL, some without
      - empty collections, unicode keys/values, single-char keys
      - duplicate value shapes to ensure all branches are exercised
    """
    store = KvStore()

    # Ensure at least one of each value type and edge case.
    store.set("empty_list_key", [])
    store.set("empty_set_key", set())
    store.set("empty_str_key", "")
    store.set("unicode_key_café", "unicode value ñ")
    store.set("unicode_val", "日本語テスト")
    store.set("with_ttl_str", "expires", ttl=3600)
    store.set("with_ttl_list", ["a", "b"], ttl=60)
    store.set("with_ttl_set", {"x", "y", "z"}, ttl=120)
    store.set("single_char", "v")
    store.set("a", "short key")

    # Large random population.
    seen_keys = set()
    for _ in range(keys):
        k = _rand_str(rng, min_len=1, max_len=16)
        if k in seen_keys:
            continue
        seen_keys.add(k)
        v = _rand_value(rng)
        ttl = rng.choice([None, None, None, 30, 300, 9999])
        store.set(k, v, ttl=ttl)

    return store


# ---------------------------------------------------------------------------
# Roundtrip identity: the primary tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fmt", ["json", "binary"])
def test_save_load_roundtrip_identity(tmp_path, fmt):
    """
    Save a rich, seeded store and reload it; the full canonical state must
    be identical — keys, values of every type, and TTLs included.

    Uses structural equality on sorted canonical forms rather than a hash so
    that failures produce a readable diff showing exactly which record changed.
    """
    store = build_seeded_store(random.Random(42), keys=200)
    before = canonical_dump(store)

    path = tmp_path / f"store.{fmt}"
    save(store, path, format=fmt)
    reloaded = load(path, format=fmt)

    after = canonical_dump(reloaded)
    assert after == before, (
        f"Roundtrip identity failed for format={fmt!r}.\n"
        f"Before ({len(before)} entries):\n{before[:10]}...\n"
        f"After  ({len(after)} entries):\n{after[:10]}..."
    )


@pytest.mark.parametrize("fmt", ["json", "binary"])
def test_roundtrip_different_seeds_are_independent(tmp_path, fmt):
    """
    Two differently-seeded stores saved under different paths must reload
    to their own state, not each other's. Guards against accidental path
    collisions or global mutable state in the module.
    """
    store_a = build_seeded_store(random.Random(1), keys=50)
    store_b = build_seeded_store(random.Random(2), keys=50)

    path_a = tmp_path / f"a.{fmt}"
    path_b = tmp_path / f"b.{fmt}"

    save(store_a, path_a, format=fmt)
    save(store_b, path_b, format=fmt)

    reloaded_a = load(path_a, format=fmt)
    reloaded_b = load(path_b, format=fmt)

    assert canonical_dump(reloaded_a) == canonical_dump(store_a)
    assert canonical_dump(reloaded_b) == canonical_dump(store_b)
    # Sanity: the two stores are not accidentally identical.
    assert canonical_dump(store_a) != canonical_dump(store_b)


# ---------------------------------------------------------------------------
# Value-type coverage: each type survives a roundtrip
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fmt", ["json", "binary"])
@pytest.mark.parametrize("key,value", [
    ("str_plain", "hello"),
    ("str_empty", ""),
    ("str_unicode", "日本語 café emoji🎉"),
    ("str_spaces", "  leading and trailing  "),
    ("list_ints_as_str", ["1", "2", "3"]),
    ("list_empty", []),
    ("list_single", ["only"]),
    ("list_unicode", ["α", "β", "γ"]),
    ("list_duplicates", ["a", "a", "b"]),
    ("set_basic", {"x", "y", "z"}),
    ("set_empty", set()),
    ("set_single", {"solo"}),
    ("set_unicode", {"π", "∑", "∞"}),
])
def test_value_type_roundtrip(tmp_path, fmt, key, value):
    """
    Each supported value type and shape survives save→load unchanged.
    Parameterized so failures point to the exact type and format.
    """
    store = KvStore()
    store.set(key, value)

    path = tmp_path / f"single.{fmt}"
    save(store, path, format=fmt)
    reloaded = load(path, format=fmt)

    assert reloaded.get(key) == value


# ---------------------------------------------------------------------------
# TTL persistence
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fmt", ["json", "binary"])
@pytest.mark.parametrize("ttl", [1, 60, 3600, 86400, 0])
def test_ttl_preserved_after_roundtrip(tmp_path, fmt, ttl):
    """
    TTL values are persisted and recovered exactly.
    """
    store = KvStore()
    store.set("k", "v", ttl=ttl)

    path = tmp_path / f"ttl.{fmt}"
    save(store, path, format=fmt)
    reloaded = load(path, format=fmt)

    items = list(reloaded.items())
    assert len(items) == 1
    key, value, loaded_ttl = items[0]
    assert key == "k"
    assert value == "v"
    assert loaded_ttl == ttl


@pytest.mark.parametrize("fmt", ["json", "binary"])
def test_no_ttl_preserved_after_roundtrip(tmp_path, fmt):
    """
    A key set without TTL reloads with TTL of None (not 0, not omitted).
    """
    store = KvStore()
    store.set("k", "v")

    path = tmp_path / f"nottl.{fmt}"
    save(store, path, format=fmt)
    reloaded = load(path, format=fmt)

    items = list(reloaded.items())
    assert len(items) == 1
    key, value, loaded_ttl = items[0]
    assert key == "k"
    assert loaded_ttl is None


@pytest.mark.parametrize("fmt", ["json", "binary"])
def test_mixed_ttl_and_no_ttl(tmp_path, fmt):
    """
    A store with some keys having TTL and others without correctly preserves
    the distinction for every key after a roundtrip.
    """
    store = KvStore()
    store.set("no_ttl_str", "plain")
    store.set("no_ttl_list", ["a", "b"])
    store.set("no_ttl_set", {"x"})
    store.set("ttl_str", "expires", ttl=100)
    store.set("ttl_list", ["c"], ttl=200)
    store.set("ttl_set", {"y"}, ttl=300)

    path = tmp_path / f"mixed.{fmt}"
    save(store, path, format=fmt)
    reloaded = load(path, format=fmt)

    reloaded_by_key = {k: (v, t) for k, v, t in reloaded.items()}

    assert reloaded_by_key["no_ttl_str"] == ("plain", None)
    assert reloaded_by_key["no_ttl_list"] == (["a", "b"], None)
    assert reloaded_by_key["no_ttl_set"] == ({"x"}, None)
    assert reloaded_by_key["ttl_str"] == ("expires", 100)
    assert reloaded_by_key["ttl_list"] == (["c"], 200)
    assert reloaded_by_key["ttl_set"] == ({"y"}, 300)


# ---------------------------------------------------------------------------
# Empty store
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fmt", ["json", "binary"])
def test_empty_store_roundtrip(tmp_path, fmt):
    """
    Saving and loading an empty store yields an empty store (no phantom keys).
    """
    store = KvStore()
    path = tmp_path / f"empty.{fmt}"
    save(store, path, format=fmt)
    reloaded = load(path, format=fmt)

    assert list(reloaded.items()) == []


# ---------------------------------------------------------------------------
# Key edge cases
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fmt", ["json", "binary"])
@pytest.mark.parametrize("key", [
    "simple",
    "with spaces",
    "unicode/日本語",
    "dots.in.key",
    "slashes/in/key",
    "a" * 256,           # long key
    "\t\n",              # whitespace-only key
    "UPPER_CASE",
    "123numeric",
])
def test_key_edge_cases_roundtrip(tmp_path, fmt, key):
    """
    Keys with unusual characters, lengths, or encodings survive a roundtrip.
    """
    store = KvStore()
    store.set(key, "value")

    path = tmp_path / f"keys.{fmt}"
    save(store, path, format=fmt)
    reloaded = load(path, format=fmt)

    assert reloaded.get(key) == "value"


# ---------------------------------------------------------------------------
# Overwrite and re-save
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fmt", ["json", "binary"])
def test_save_overwrites_existing_file(tmp_path, fmt):
    """
    Saving a new store to an existing path replaces the old data completely;
    loading retrieves the new state, not a merge or the old state.
    """
    path = tmp_path / f"overwrite.{fmt}"

    store1 = KvStore()
    store1.set("old_key", "old_value")
    save(store1, path, format=fmt)

    store2 = KvStore()
    store2.set("new_key", "new_value")
    save(store2, path, format=fmt)

    reloaded = load(path, format=fmt)
    reloaded_by_key = {k: v for k, v, _ in reloaded.items()}

    assert "new_key" in reloaded_by_key
    assert reloaded_by_key["new_key"] == "new_value"
    assert "old_key" not in reloaded_by_key


# ---------------------------------------------------------------------------
# Format isolation: files are not cross-loadable
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("save_fmt,load_fmt", [
    ("json", "binary"),
    ("binary", "json"),
])
def test_format_mismatch_raises(tmp_path, save_fmt, load_fmt):
    """
    Loading a file with the wrong format must raise an exception rather than
    silently returning corrupt or empty data.
    """
    store = KvStore()
    store.set("k", "v")

    path = tmp_path / "mismatch"
    save(store, path, format=save_fmt)

    with pytest.raises(Exception):
        load(path, format=load_fmt)


# ---------------------------------------------------------------------------
# Large-scale seeded roundtrip for additional confidence
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fmt", ["json", "binary"])
def test_large_store_roundtrip(tmp_path, fmt):
    """
    A large store (500 keys, all types, unicode, TTL mix) survives a complete
    roundtrip. Uses a different seed from the primary test to maximize coverage.
    """
    store = build_seeded_store(random.Random(9999), keys=500)
    before = canonical_dump(store)

    path = tmp_path / f"large.{fmt}"
    save(store, path, format=fmt)
    reloaded = load(path, format=fmt)

    assert canonical_dump(reloaded) == before


# ---------------------------------------------------------------------------
# Cross-format identity: same logical state persists equivalently
# ---------------------------------------------------------------------------

def test_json_and_binary_preserve_same_state(tmp_path):
    """
    Saving the same store in JSON and binary and reloading both yields the
    same canonical state. Validates that neither format introduces data loss
    relative to the other.
    """
    store = build_seeded_store(random.Random(7777), keys=100)
    before = canonical_dump(store)

    json_path = tmp_path / "store.json"
    bin_path = tmp_path / "store.bin"

    save(store, json_path, format="json")
    save(store, bin_path, format="binary")

    reloaded_json = load(json_path, format="json")
    reloaded_bin = load(bin_path, format="binary")

    assert canonical_dump(reloaded_json) == before
    assert canonical_dump(reloaded_bin) == before
    assert canonical_dump(reloaded_json) == canonical_dump(reloaded_bin)
