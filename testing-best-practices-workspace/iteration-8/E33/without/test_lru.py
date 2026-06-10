"""
Tests for LruCache using differential / pirate-testing techniques.

Since no external reference implementation is available, we use two
complementary strategies drawn from the guidance:

1. **Self-differential (roundtrip oracle)**: build a plain Python reference
   `RefLruCache` backed by `collections.OrderedDict` inline in this file.
   Every property test runs the same sequence on *both* caches and asserts
   they agree.  The reference is the oracle — no hard-coded expected values
   are required.

2. **Data-driven conformance (pirate-style)**: operation sequences are
   expressed as plain data (list of dicts).  The harness replays them on the
   implementation under test and on the reference, comparing results at every
   step.  Adding new scenarios requires only adding a new data entry.
"""

import pytest
from collections import OrderedDict
from lru import LruCache


# ---------------------------------------------------------------------------
# Inline reference implementation (the oracle)
# ---------------------------------------------------------------------------

class RefLruCache:
    """Minimal, obviously-correct LRU cache using OrderedDict."""

    def __init__(self, capacity: int):
        self._cap = capacity
        self._store: OrderedDict = OrderedDict()

    def put(self, key, value):
        if key in self._store:
            self._store.move_to_end(key)
        self._store[key] = value
        if len(self._store) > self._cap:
            self._store.popitem(last=False)

    def get(self, key):
        if key not in self._store:
            return None
        self._store.move_to_end(key)
        return self._store[key]

    def items(self):
        return list(self._store.items())

    def __len__(self):
        return len(self._store)


# ---------------------------------------------------------------------------
# Helper: replay an operation sequence on both caches, comparing at each step
# ---------------------------------------------------------------------------

def _make_pair(capacity: int):
    return LruCache(capacity), RefLruCache(capacity)


def _replay(ops, capacity: int):
    """
    Replay a list of operation dicts on both the real and reference cache,
    asserting they produce identical observable state after each operation.

    Each op dict has a key "op" and optional "key", "value" fields.
    Supported ops: "put", "get", "len", "items".
    """
    real, ref = _make_pair(capacity)
    for op in ops:
        name = op["op"]
        if name == "put":
            real.put(op["key"], op["value"])
            ref.put(op["key"], op["value"])
        elif name == "get":
            assert real.get(op["key"]) == ref.get(op["key"]), (
                f'get({op["key"]!r}) diverged'
            )
        elif name == "len":
            assert len(real) == len(ref), "len() diverged"
        elif name == "items":
            assert real.items() == ref.items(), "items() diverged"
        else:
            raise ValueError(f"Unknown op: {name!r}")

        # After *every* operation, full state must agree.
        assert real.items() == ref.items(), (
            f"State diverged after op {op!r}: "
            f"real={real.items()}, ref={ref.items()}"
        )
        assert len(real) == len(ref)


# ---------------------------------------------------------------------------
# Conformance scenarios (pirate / data-driven)
# Each scenario is a dict with "capacity" and "ops".
# ---------------------------------------------------------------------------

CONFORMANCE_SCENARIOS = [
    {
        "id": "basic_put_get",
        "capacity": 3,
        "ops": [
            {"op": "put", "key": "a", "value": 1},
            {"op": "get", "key": "a"},
            {"op": "get", "key": "missing"},
            {"op": "len"},
        ],
    },
    {
        "id": "eviction_lru_order",
        "capacity": 2,
        "ops": [
            {"op": "put", "key": "x", "value": 10},
            {"op": "put", "key": "y", "value": 20},
            # x is now LRU; adding z should evict x
            {"op": "put", "key": "z", "value": 30},
            {"op": "get", "key": "x"},   # should be None
            {"op": "get", "key": "y"},
            {"op": "get", "key": "z"},
            {"op": "len"},
            {"op": "items"},
        ],
    },
    {
        "id": "get_refreshes_recency",
        "capacity": 2,
        "ops": [
            {"op": "put", "key": "a", "value": 1},
            {"op": "put", "key": "b", "value": 2},
            # access 'a' so 'b' becomes LRU
            {"op": "get", "key": "a"},
            {"op": "put", "key": "c", "value": 3},  # should evict 'b'
            {"op": "get", "key": "a"},   # still present
            {"op": "get", "key": "b"},   # evicted → None
            {"op": "get", "key": "c"},   # present
            {"op": "items"},
        ],
    },
    {
        "id": "put_updates_existing_key",
        "capacity": 3,
        "ops": [
            {"op": "put", "key": "k", "value": 1},
            {"op": "put", "key": "k", "value": 99},
            {"op": "get", "key": "k"},
            {"op": "len"},
        ],
    },
    {
        "id": "overwrite_refreshes_recency",
        "capacity": 2,
        "ops": [
            {"op": "put", "key": "a", "value": 1},
            {"op": "put", "key": "b", "value": 2},
            # overwrite 'a' — it should become MRU; 'b' becomes LRU
            {"op": "put", "key": "a", "value": 100},
            {"op": "put", "key": "c", "value": 3},  # should evict 'b'
            {"op": "get", "key": "a"},
            {"op": "get", "key": "b"},   # evicted → None
            {"op": "get", "key": "c"},
            {"op": "items"},
        ],
    },
    {
        "id": "capacity_one",
        "capacity": 1,
        "ops": [
            {"op": "put", "key": "a", "value": 1},
            {"op": "put", "key": "b", "value": 2},
            {"op": "get", "key": "a"},   # evicted
            {"op": "get", "key": "b"},
            {"op": "len"},
        ],
    },
    {
        "id": "repeated_gets_do_not_grow_cache",
        "capacity": 2,
        "ops": [
            {"op": "put", "key": "a", "value": 1},
            {"op": "get", "key": "a"},
            {"op": "get", "key": "a"},
            {"op": "get", "key": "a"},
            {"op": "len"},
            {"op": "items"},
        ],
    },
    {
        "id": "fill_to_capacity_no_eviction_yet",
        "capacity": 4,
        "ops": [
            {"op": "put", "key": 1, "value": "one"},
            {"op": "put", "key": 2, "value": "two"},
            {"op": "put", "key": 3, "value": "three"},
            {"op": "put", "key": 4, "value": "four"},
            {"op": "len"},
            {"op": "items"},
        ],
    },
    {
        "id": "many_evictions_sequential",
        "capacity": 2,
        "ops": [
            {"op": "put", "key": i, "value": i * 10}
            for i in range(10)
        ] + [
            {"op": "len"},
            {"op": "get", "key": 8},
            {"op": "get", "key": 9},
            {"op": "get", "key": 0},   # long evicted
        ],
    },
    {
        "id": "mixed_key_types_strings_and_ints",
        "capacity": 3,
        "ops": [
            {"op": "put", "key": "one", "value": 1},
            {"op": "put", "key": 2,     "value": "two"},
            {"op": "put", "key": (3,),  "value": [3]},
            {"op": "get", "key": "one"},
            {"op": "get", "key": 2},
            {"op": "get", "key": (3,)},
            {"op": "items"},
        ],
    },
    {
        "id": "none_value_stored_and_retrieved",
        "capacity": 2,
        "ops": [
            {"op": "put", "key": "a", "value": None},
            {"op": "get", "key": "a"},
            {"op": "len"},
        ],
    },
    {
        "id": "zero_value_not_confused_with_missing",
        "capacity": 2,
        "ops": [
            {"op": "put", "key": "z", "value": 0},
            {"op": "get", "key": "z"},
            {"op": "get", "key": "missing"},
            {"op": "len"},
        ],
    },
    {
        "id": "get_on_empty_cache",
        "capacity": 3,
        "ops": [
            {"op": "get", "key": "anything"},
            {"op": "len"},
        ],
    },
    {
        "id": "lru_among_three_eviction_chain",
        "capacity": 3,
        "ops": [
            {"op": "put", "key": "a", "value": 1},
            {"op": "put", "key": "b", "value": 2},
            {"op": "put", "key": "c", "value": 3},
            # access order: b, c, a  →  b becomes oldest unused
            {"op": "get", "key": "b"},
            {"op": "get", "key": "c"},
            {"op": "get", "key": "a"},
            # now add d → 'b' (oldest since last access) should be evicted... wait,
            # after above gets: recency = b < c < a.  d evicts b.
            {"op": "put", "key": "d", "value": 4},
            {"op": "get", "key": "b"},   # evicted
            {"op": "get", "key": "c"},
            {"op": "get", "key": "a"},
            {"op": "get", "key": "d"},
            {"op": "items"},
        ],
    },
]


@pytest.mark.parametrize(
    "scenario",
    CONFORMANCE_SCENARIOS,
    ids=[s["id"] for s in CONFORMANCE_SCENARIOS],
)
def test_conformance_scenario(scenario):
    """
    Pirate-style: replay each data-driven scenario on both the implementation
    under test and the inline reference, asserting they agree at every step.
    """
    _replay(scenario["ops"], scenario["capacity"])


# ---------------------------------------------------------------------------
# Focused differential tests (same computation, two implementations)
# ---------------------------------------------------------------------------

class TestDifferentialPutGet:
    """Put/get behaviour matches the reference oracle."""

    def test_single_entry(self):
        real, ref = _make_pair(5)
        real.put("hello", 42)
        ref.put("hello", 42)
        assert real.get("hello") == ref.get("hello")

    def test_missing_key_returns_none(self):
        real, ref = _make_pair(5)
        assert real.get("nope") == ref.get("nope") == None

    def test_overwrite_returns_new_value(self):
        real, ref = _make_pair(5)
        for cache in (real, ref):
            cache.put("k", 1)
            cache.put("k", 2)
        assert real.get("k") == ref.get("k") == 2

    def test_len_after_puts(self):
        real, ref = _make_pair(5)
        for i in range(4):
            real.put(i, i)
            ref.put(i, i)
        assert len(real) == len(ref)

    def test_items_order_matches_reference(self):
        real, ref = _make_pair(5)
        for cache in (real, ref):
            cache.put("a", 1)
            cache.put("b", 2)
            cache.put("c", 3)
        assert real.items() == ref.items()


class TestDifferentialEviction:
    """Eviction behaviour matches the reference oracle."""

    def test_evicts_lru_on_overflow(self):
        real, ref = _make_pair(2)
        for cache in (real, ref):
            cache.put(1, "a")
            cache.put(2, "b")
            cache.put(3, "c")  # should evict 1
        assert real.get(1) == ref.get(1) == None
        assert real.get(2) == ref.get(2)
        assert real.get(3) == ref.get(3)

    def test_get_prevents_eviction(self):
        real, ref = _make_pair(2)
        for cache in (real, ref):
            cache.put("a", 1)
            cache.put("b", 2)
            cache.get("a")      # refresh 'a'; 'b' becomes LRU
            cache.put("c", 3)   # should evict 'b'
        assert real.get("b") == ref.get("b") == None
        assert real.get("a") == ref.get("a")
        assert real.get("c") == ref.get("c")

    def test_put_existing_key_prevents_eviction(self):
        real, ref = _make_pair(2)
        for cache in (real, ref):
            cache.put("a", 1)
            cache.put("b", 2)
            cache.put("a", 10)  # refresh 'a'; 'b' becomes LRU
            cache.put("c", 3)   # should evict 'b'
        assert real.get("b") == ref.get("b") == None
        assert real.get("a") == ref.get("a")

    def test_capacity_one_always_keeps_latest(self):
        real, ref = _make_pair(1)
        for i in range(5):
            real.put(i, i)
            ref.put(i, i)
            assert real.items() == ref.items()
            assert len(real) == len(ref) == 1

    def test_no_eviction_below_capacity(self):
        cap = 5
        real, ref = _make_pair(cap)
        for i in range(cap):
            real.put(i, i)
            ref.put(i, i)
        assert len(real) == len(ref) == cap
        assert real.items() == ref.items()


class TestDifferentialItems:
    """items() reflects insertion / access order matching the reference."""

    def test_items_empty_cache(self):
        real, ref = _make_pair(3)
        assert real.items() == ref.items() == []

    def test_items_after_sequential_puts(self):
        real, ref = _make_pair(5)
        for cache in (real, ref):
            for k, v in [("x", 1), ("y", 2), ("z", 3)]:
                cache.put(k, v)
        assert real.items() == ref.items()

    def test_items_reflects_eviction(self):
        real, ref = _make_pair(2)
        for cache in (real, ref):
            cache.put("a", 1)
            cache.put("b", 2)
            cache.put("c", 3)
        assert real.items() == ref.items()

    def test_items_after_access_reorder(self):
        real, ref = _make_pair(3)
        for cache in (real, ref):
            cache.put("a", 1)
            cache.put("b", 2)
            cache.put("c", 3)
            cache.get("a")   # move 'a' to MRU end
        assert real.items() == ref.items()


class TestDifferentialLen:
    """__len__ always matches the reference."""

    def test_len_empty(self):
        real, ref = _make_pair(3)
        assert len(real) == len(ref) == 0

    def test_len_grows_with_puts(self):
        real, ref = _make_pair(10)
        for i in range(7):
            real.put(i, i)
            ref.put(i, i)
            assert len(real) == len(ref)

    def test_len_capped_at_capacity(self):
        cap = 3
        real, ref = _make_pair(cap)
        for i in range(10):
            real.put(i, i)
            ref.put(i, i)
        assert len(real) == len(ref) == cap

    def test_len_unchanged_by_overwrite(self):
        real, ref = _make_pair(3)
        for cache in (real, ref):
            cache.put("a", 1)
            cache.put("b", 2)
        size_before = len(ref)
        real.put("a", 99)
        ref.put("a", 99)
        assert len(real) == len(ref) == size_before

    def test_len_unchanged_by_get(self):
        real, ref = _make_pair(3)
        for cache in (real, ref):
            cache.put("a", 1)
        real.get("a")
        ref.get("a")
        assert len(real) == len(ref)


# ---------------------------------------------------------------------------
# Roundtrip / self-differential: write then read back
# ---------------------------------------------------------------------------

class TestRoundtrip:
    """Values written are exactly the values read back (roundtrip oracle)."""

    @pytest.mark.parametrize("key,value", [
        ("string_key", "string_value"),
        (42, 3.14),
        ("k", [1, 2, 3]),
        ("k2", {"nested": True}),
        ("k3", None),
        ("k4", 0),
        ("k5", False),
        ("k6", ""),
    ])
    def test_put_then_get_roundtrip(self, key, value):
        cache = LruCache(10)
        cache.put(key, value)
        assert cache.get(key) == value

    def test_items_roundtrip_all_inserted(self):
        pairs = [(f"key{i}", i * 7) for i in range(5)]
        cache = LruCache(10)
        for k, v in pairs:
            cache.put(k, v)
        result = dict(cache.items())
        for k, v in pairs:
            assert result[k] == v

    def test_overwrite_roundtrip(self):
        cache = LruCache(5)
        cache.put("x", "original")
        cache.put("x", "updated")
        assert cache.get("x") == "updated"

    def test_large_value_roundtrip(self):
        big = list(range(1000))
        cache = LruCache(5)
        cache.put("big", big)
        assert cache.get("big") == big
