"""
Tests for kvstore persistence (save/load) in both 'json' and 'binary' formats.

Snapshot tests are used where the output has many fields or structural shape
matters. Specific assertions are used for simple boolean/single-value properties.
"""

import os
import pytest
from syrupy.assertion import SnapshotAssertion
from kvstore import KvStore, save, load


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_path_json(tmp_path):
    return str(tmp_path / "store.json")


@pytest.fixture
def tmp_path_binary(tmp_path):
    return str(tmp_path / "store.bin")


def store_items_as_sorted_dict(store):
    """Return a stable, sorted representation of store contents for snapshots."""
    items = list(store.items())
    # Sort by key so iteration order does not cause spurious diffs
    items.sort(key=lambda t: t[0])
    return [{"key": k, "value": sorted(v) if isinstance(v, (set, list)) else v, "ttl": ttl}
            for k, ttl, *_ in [("placeholder",)]  # placeholder to keep linter happy
            for k, v, ttl in [items[i] for i in range(len(items))]]


def store_to_snapshot_repr(store):
    """
    Return a stable string representation of store contents suitable for
    snapshot assertion. Sets are sorted, keys are sorted alphabetically.
    """
    rows = []
    items = sorted(store.items(), key=lambda t: t[0])
    for key, value, ttl in items:
        if isinstance(value, set):
            value_repr = sorted(value)
        elif isinstance(value, list):
            value_repr = list(value)
        else:
            value_repr = value
        rows.append({"key": key, "value": value_repr, "ttl": ttl})
    return rows


# ---------------------------------------------------------------------------
# Round-trip: JSON format
# ---------------------------------------------------------------------------

class TestJsonRoundTrip:
    def test_string_value_survives_json_roundtrip(self, tmp_path_json):
        store = KvStore()
        store.set("greeting", "hello")
        save(store, tmp_path_json, format="json")
        loaded = load(tmp_path_json, format="json")
        assert loaded.get("greeting") == "hello"

    def test_list_value_survives_json_roundtrip(self, tmp_path_json):
        store = KvStore()
        store.set("colors", ["red", "green", "blue"])
        save(store, tmp_path_json, format="json")
        loaded = load(tmp_path_json, format="json")
        assert loaded.get("colors") == ["red", "green", "blue"]

    def test_set_value_survives_json_roundtrip(self, tmp_path_json):
        store = KvStore()
        store.set("tags", {"alpha", "beta", "gamma"})
        save(store, tmp_path_json, format="json")
        loaded = load(tmp_path_json, format="json")
        assert loaded.get("tags") == {"alpha", "beta", "gamma"}

    def test_ttl_survives_json_roundtrip(self, tmp_path_json):
        store = KvStore()
        store.set("session", "tok123", ttl=300)
        save(store, tmp_path_json, format="json")
        loaded = load(tmp_path_json, format="json")
        _, _, ttl = next(t for t in loaded.items() if t[0] == "session")
        assert ttl == 300

    def test_none_ttl_survives_json_roundtrip(self, tmp_path_json):
        store = KvStore()
        store.set("permanent", "value")
        save(store, tmp_path_json, format="json")
        loaded = load(tmp_path_json, format="json")
        _, _, ttl = next(t for t in loaded.items() if t[0] == "permanent")
        assert ttl is None

    def test_multiple_keys_survive_json_roundtrip(self, tmp_path_json):
        store = KvStore()
        store.set("a", "alpha")
        store.set("b", ["x", "y"])
        store.set("c", {"p", "q"})
        store.set("d", "delta", ttl=60)
        save(store, tmp_path_json, format="json")
        loaded = load(tmp_path_json, format="json")
        assert loaded.get("a") == "alpha"
        assert loaded.get("b") == ["x", "y"]
        assert loaded.get("c") == {"p", "q"}
        assert loaded.get("d") == "delta"

    def test_empty_store_json_roundtrip(self, tmp_path_json):
        store = KvStore()
        save(store, tmp_path_json, format="json")
        loaded = load(tmp_path_json, format="json")
        assert list(loaded.items()) == []

    def test_empty_string_value_json_roundtrip(self, tmp_path_json):
        store = KvStore()
        store.set("empty", "")
        save(store, tmp_path_json, format="json")
        loaded = load(tmp_path_json, format="json")
        assert loaded.get("empty") == ""

    def test_empty_list_value_json_roundtrip(self, tmp_path_json):
        store = KvStore()
        store.set("emptylist", [])
        save(store, tmp_path_json, format="json")
        loaded = load(tmp_path_json, format="json")
        assert loaded.get("emptylist") == []

    def test_empty_set_value_json_roundtrip(self, tmp_path_json):
        store = KvStore()
        store.set("emptyset", set())
        save(store, tmp_path_json, format="json")
        loaded = load(tmp_path_json, format="json")
        assert loaded.get("emptyset") == set()

    def test_key_with_special_characters_json_roundtrip(self, tmp_path_json):
        store = KvStore()
        store.set("key with spaces/and:special", "v")
        save(store, tmp_path_json, format="json")
        loaded = load(tmp_path_json, format="json")
        assert loaded.get("key with spaces/and:special") == "v"

    def test_unicode_values_json_roundtrip(self, tmp_path_json):
        store = KvStore()
        store.set("greeting", "こんにちは")
        save(store, tmp_path_json, format="json")
        loaded = load(tmp_path_json, format="json")
        assert loaded.get("greeting") == "こんにちは"


# ---------------------------------------------------------------------------
# Round-trip: binary format
# ---------------------------------------------------------------------------

class TestBinaryRoundTrip:
    def test_string_value_survives_binary_roundtrip(self, tmp_path_binary):
        store = KvStore()
        store.set("greeting", "hello")
        save(store, tmp_path_binary, format="binary")
        loaded = load(tmp_path_binary, format="binary")
        assert loaded.get("greeting") == "hello"

    def test_list_value_survives_binary_roundtrip(self, tmp_path_binary):
        store = KvStore()
        store.set("colors", ["red", "green", "blue"])
        save(store, tmp_path_binary, format="binary")
        loaded = load(tmp_path_binary, format="binary")
        assert loaded.get("colors") == ["red", "green", "blue"]

    def test_set_value_survives_binary_roundtrip(self, tmp_path_binary):
        store = KvStore()
        store.set("tags", {"alpha", "beta", "gamma"})
        save(store, tmp_path_binary, format="binary")
        loaded = load(tmp_path_binary, format="binary")
        assert loaded.get("tags") == {"alpha", "beta", "gamma"}

    def test_ttl_survives_binary_roundtrip(self, tmp_path_binary):
        store = KvStore()
        store.set("session", "tok123", ttl=300)
        save(store, tmp_path_binary, format="binary")
        loaded = load(tmp_path_binary, format="binary")
        _, _, ttl = next(t for t in loaded.items() if t[0] == "session")
        assert ttl == 300

    def test_none_ttl_survives_binary_roundtrip(self, tmp_path_binary):
        store = KvStore()
        store.set("permanent", "value")
        save(store, tmp_path_binary, format="binary")
        loaded = load(tmp_path_binary, format="binary")
        _, _, ttl = next(t for t in loaded.items() if t[0] == "permanent")
        assert ttl is None

    def test_multiple_keys_survive_binary_roundtrip(self, tmp_path_binary):
        store = KvStore()
        store.set("a", "alpha")
        store.set("b", ["x", "y"])
        store.set("c", {"p", "q"})
        store.set("d", "delta", ttl=60)
        save(store, tmp_path_binary, format="binary")
        loaded = load(tmp_path_binary, format="binary")
        assert loaded.get("a") == "alpha"
        assert loaded.get("b") == ["x", "y"]
        assert loaded.get("c") == {"p", "q"}
        assert loaded.get("d") == "delta"

    def test_empty_store_binary_roundtrip(self, tmp_path_binary):
        store = KvStore()
        save(store, tmp_path_binary, format="binary")
        loaded = load(tmp_path_binary, format="binary")
        assert list(loaded.items()) == []

    def test_unicode_values_binary_roundtrip(self, tmp_path_binary):
        store = KvStore()
        store.set("greeting", "こんにちは")
        save(store, tmp_path_binary, format="binary")
        loaded = load(tmp_path_binary, format="binary")
        assert loaded.get("greeting") == "こんにちは"


# ---------------------------------------------------------------------------
# Snapshot tests: full store shape after round-trip
# ---------------------------------------------------------------------------

class TestPersistenceSnapshot:
    def test_mixed_store_json_snapshot(self, tmp_path_json, snapshot):
        """
        Snapshot captures the stable shape of a store with all value types
        and mixed TTL settings after a JSON round-trip.
        """
        store = KvStore()
        store.set("flag", "enabled")
        store.set("scores", [10, 20, 30])
        store.set("roles", {"admin", "editor"})
        store.set("session_token", "abc123", ttl=600)
        store.set("cache_key", "xyz", ttl=30)
        save(store, tmp_path_json, format="json")
        loaded = load(tmp_path_json, format="json")
        assert store_to_snapshot_repr(loaded) == snapshot

    def test_mixed_store_binary_snapshot(self, tmp_path_binary, snapshot):
        """
        Snapshot captures the stable shape of a store with all value types
        and mixed TTL settings after a binary round-trip.
        """
        store = KvStore()
        store.set("flag", "enabled")
        store.set("scores", [10, 20, 30])
        store.set("roles", {"admin", "editor"})
        store.set("session_token", "abc123", ttl=600)
        store.set("cache_key", "xyz", ttl=30)
        save(store, tmp_path_binary, format="binary")
        loaded = load(tmp_path_binary, format="binary")
        assert store_to_snapshot_repr(loaded) == snapshot

    def test_all_value_types_json_snapshot(self, tmp_path_json, snapshot):
        """
        Snapshot covers string, list, and set values without TTL to verify
        type fidelity is preserved in the JSON format.
        """
        store = KvStore()
        store.set("str_key", "just a string")
        store.set("list_key", ["a", "b", "c"])
        store.set("set_key", {"x", "y", "z"})
        save(store, tmp_path_json, format="json")
        loaded = load(tmp_path_json, format="json")
        assert store_to_snapshot_repr(loaded) == snapshot

    def test_all_value_types_binary_snapshot(self, tmp_path_binary, snapshot):
        """
        Snapshot covers string, list, and set values without TTL to verify
        type fidelity is preserved in the binary format.
        """
        store = KvStore()
        store.set("str_key", "just a string")
        store.set("list_key", ["a", "b", "c"])
        store.set("set_key", {"x", "y", "z"})
        save(store, tmp_path_binary, format="binary")
        loaded = load(tmp_path_binary, format="binary")
        assert store_to_snapshot_repr(loaded) == snapshot


# ---------------------------------------------------------------------------
# File creation / existence
# ---------------------------------------------------------------------------

class TestFileCreation:
    def test_save_json_creates_file(self, tmp_path_json):
        store = KvStore()
        store.set("k", "v")
        assert not os.path.exists(tmp_path_json)
        save(store, tmp_path_json, format="json")
        assert os.path.exists(tmp_path_json)

    def test_save_binary_creates_file(self, tmp_path_binary):
        store = KvStore()
        store.set("k", "v")
        assert not os.path.exists(tmp_path_binary)
        save(store, tmp_path_binary, format="binary")
        assert os.path.exists(tmp_path_binary)

    def test_json_file_is_not_empty_after_save(self, tmp_path_json):
        store = KvStore()
        store.set("k", "v")
        save(store, tmp_path_json, format="json")
        assert os.path.getsize(tmp_path_json) > 0

    def test_binary_file_is_not_empty_after_save(self, tmp_path_binary):
        store = KvStore()
        store.set("k", "v")
        save(store, tmp_path_binary, format="binary")
        assert os.path.getsize(tmp_path_binary) > 0

    def test_save_overwrites_existing_json_file(self, tmp_path_json):
        store1 = KvStore()
        store1.set("only_key", "first")
        save(store1, tmp_path_json, format="json")

        store2 = KvStore()
        store2.set("only_key", "second")
        save(store2, tmp_path_json, format="json")

        loaded = load(tmp_path_json, format="json")
        assert loaded.get("only_key") == "second"

    def test_save_overwrites_existing_binary_file(self, tmp_path_binary):
        store1 = KvStore()
        store1.set("only_key", "first")
        save(store1, tmp_path_binary, format="binary")

        store2 = KvStore()
        store2.set("only_key", "second")
        save(store2, tmp_path_binary, format="binary")

        loaded = load(tmp_path_binary, format="binary")
        assert loaded.get("only_key") == "second"


# ---------------------------------------------------------------------------
# Key count preservation
# ---------------------------------------------------------------------------

class TestKeyCountPreservation:
    def test_all_keys_present_after_json_roundtrip(self, tmp_path_json):
        store = KvStore()
        keys = ["alpha", "beta", "gamma", "delta", "epsilon"]
        for k in keys:
            store.set(k, k + "_value")
        save(store, tmp_path_json, format="json")
        loaded = load(tmp_path_json, format="json")
        loaded_keys = {k for k, _, _ in loaded.items()}
        assert loaded_keys == set(keys)

    def test_all_keys_present_after_binary_roundtrip(self, tmp_path_binary):
        store = KvStore()
        keys = ["alpha", "beta", "gamma", "delta", "epsilon"]
        for k in keys:
            store.set(k, k + "_value")
        save(store, tmp_path_binary, format="binary")
        loaded = load(tmp_path_binary, format="binary")
        loaded_keys = {k for k, _, _ in loaded.items()}
        assert loaded_keys == set(keys)

    def test_no_extra_keys_after_json_roundtrip(self, tmp_path_json):
        store = KvStore()
        store.set("only", "one")
        save(store, tmp_path_json, format="json")
        loaded = load(tmp_path_json, format="json")
        loaded_keys = [k for k, _, _ in loaded.items()]
        assert len(loaded_keys) == 1

    def test_no_extra_keys_after_binary_roundtrip(self, tmp_path_binary):
        store = KvStore()
        store.set("only", "one")
        save(store, tmp_path_binary, format="binary")
        loaded = load(tmp_path_binary, format="binary")
        loaded_keys = [k for k, _, _ in loaded.items()]
        assert len(loaded_keys) == 1


# ---------------------------------------------------------------------------
# TTL semantics across formats
# ---------------------------------------------------------------------------

class TestTTLPersistence:
    @pytest.mark.parametrize("ttl", [1, 60, 3600, 86400, 99999])
    def test_various_ttl_values_preserved_json(self, tmp_path, ttl):
        path = str(tmp_path / "store.json")
        store = KvStore()
        store.set("k", "v", ttl=ttl)
        save(store, path, format="json")
        loaded = load(path, format="json")
        _, _, loaded_ttl = next(t for t in loaded.items() if t[0] == "k")
        assert loaded_ttl == ttl

    @pytest.mark.parametrize("ttl", [1, 60, 3600, 86400, 99999])
    def test_various_ttl_values_preserved_binary(self, tmp_path, ttl):
        path = str(tmp_path / "store.bin")
        store = KvStore()
        store.set("k", "v", ttl=ttl)
        save(store, path, format="binary")
        loaded = load(path, format="binary")
        _, _, loaded_ttl = next(t for t in loaded.items() if t[0] == "k")
        assert loaded_ttl == ttl

    def test_multiple_ttls_preserved_independently_json(self, tmp_path_json):
        store = KvStore()
        store.set("short", "v", ttl=10)
        store.set("long", "v", ttl=7200)
        store.set("none", "v")
        save(store, tmp_path_json, format="json")
        loaded = load(tmp_path_json, format="json")
        items = {k: ttl for k, _, ttl in loaded.items()}
        assert items["short"] == 10
        assert items["long"] == 7200
        assert items["none"] is None

    def test_multiple_ttls_preserved_independently_binary(self, tmp_path_binary):
        store = KvStore()
        store.set("short", "v", ttl=10)
        store.set("long", "v", ttl=7200)
        store.set("none", "v")
        save(store, tmp_path_binary, format="binary")
        loaded = load(tmp_path_binary, format="binary")
        items = {k: ttl for k, _, ttl in loaded.items()}
        assert items["short"] == 10
        assert items["long"] == 7200
        assert items["none"] is None


# ---------------------------------------------------------------------------
# Value type fidelity: loaded types match original types
# ---------------------------------------------------------------------------

class TestValueTypeFidelity:
    @pytest.mark.parametrize("fmt,path_fixture", [
        ("json", "tmp_path_json"),
        ("binary", "tmp_path_binary"),
    ])
    def test_str_type_preserved(self, fmt, path_fixture, request):
        path = request.getfixturevalue(path_fixture)
        store = KvStore()
        store.set("k", "hello")
        save(store, path, format=fmt)
        loaded = load(path, format=fmt)
        assert isinstance(loaded.get("k"), str)

    @pytest.mark.parametrize("fmt,path_fixture", [
        ("json", "tmp_path_json"),
        ("binary", "tmp_path_binary"),
    ])
    def test_list_type_preserved(self, fmt, path_fixture, request):
        path = request.getfixturevalue(path_fixture)
        store = KvStore()
        store.set("k", ["a", "b"])
        save(store, path, format=fmt)
        loaded = load(path, format=fmt)
        assert isinstance(loaded.get("k"), list)

    @pytest.mark.parametrize("fmt,path_fixture", [
        ("json", "tmp_path_json"),
        ("binary", "tmp_path_binary"),
    ])
    def test_set_type_preserved(self, fmt, path_fixture, request):
        path = request.getfixturevalue(path_fixture)
        store = KvStore()
        store.set("k", {"a", "b"})
        save(store, path, format=fmt)
        loaded = load(path, format=fmt)
        assert isinstance(loaded.get("k"), set)


# ---------------------------------------------------------------------------
# Large store
# ---------------------------------------------------------------------------

class TestLargeStore:
    def test_large_store_json_roundtrip(self, tmp_path_json):
        store = KvStore()
        for i in range(500):
            store.set(f"key_{i}", f"value_{i}", ttl=i if i % 2 == 0 else None)
        save(store, tmp_path_json, format="json")
        loaded = load(tmp_path_json, format="json")
        for i in range(500):
            assert loaded.get(f"key_{i}") == f"value_{i}"

    def test_large_store_binary_roundtrip(self, tmp_path_binary):
        store = KvStore()
        for i in range(500):
            store.set(f"key_{i}", f"value_{i}", ttl=i if i % 2 == 0 else None)
        save(store, tmp_path_binary, format="binary")
        loaded = load(tmp_path_binary, format="binary")
        for i in range(500):
            assert loaded.get(f"key_{i}") == f"value_{i}"
