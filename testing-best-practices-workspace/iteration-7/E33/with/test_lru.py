"""
Tests for LruCache using a shadow-model (trivial reference) approach.

Since there is no pre-existing reference implementation, we build a deliberately
simple shadow model — a dict tracking insertion/access order — and drive both the
cache under test and the shadow model with the same seeded random operations,
asserting agreement on every observable at each step.

Additional targeted tests cover specific edge cases and behavioural contracts.
"""

import random
import pytest

from lru import LruCache


# ---------------------------------------------------------------------------
# Shadow model helpers
# ---------------------------------------------------------------------------

class ShadowLruCache:
    """
    Deliberately dumb LRU cache: obviously correct, obviously slow.
    Uses a plain list to track recency order (most-recent at the right end).
    """

    def __init__(self, capacity: int):
        assert capacity >= 1
        self._capacity = capacity
        self._data: dict = {}
        self._order: list = []  # leftmost = least recently used

    def put(self, key, value) -> None:
        if key in self._data:
            self._order.remove(key)
        self._data[key] = value
        self._order.append(key)
        if len(self._order) > self._capacity:
            evicted = self._order.pop(0)
            del self._data[evicted]

    def get(self, key):
        if key not in self._data:
            return None
        # access promotes to most-recent
        self._order.remove(key)
        self._order.append(key)
        return self._data[key]

    def items(self) -> list:
        return list(self._data.items())

    def __len__(self) -> int:
        return len(self._data)


# ---------------------------------------------------------------------------
# Shadow-model / differential tests
# ---------------------------------------------------------------------------

def _run_shadow_comparison(seed: int, capacity: int, n_ops: int,
                            key_range: int, val_range: int,
                            write_prob: float) -> None:
    """
    Drive both LruCache and ShadowLruCache with the same seeded random
    operations, asserting they agree on every observable after each operation.
    """
    rng = random.Random(seed)
    cache = LruCache(capacity=capacity)
    shadow = ShadowLruCache(capacity=capacity)

    for step in range(n_ops):
        k = rng.randrange(0, key_range)
        if rng.random() < write_prob:
            v = rng.randrange(0, val_range)
            cache.put(k, v)
            shadow.put(k, v)
        else:
            result = cache.get(k)
            expected = shadow.get(k)
            assert result == expected, (
                f"seed={seed} step={step} get({k}): "
                f"got {result!r}, expected {expected!r}"
            )

        # Check size agreement after every operation
        assert len(cache) == len(shadow), (
            f"seed={seed} step={step}: len mismatch "
            f"cache={len(cache)} shadow={len(shadow)}"
        )

        # Capacity is never exceeded
        assert len(cache) <= capacity, (
            f"seed={seed} step={step}: cache size {len(cache)} exceeds capacity {capacity}"
        )

    # Full contents must agree at the end
    assert sorted(cache.items()) == sorted(shadow.items()), (
        f"seed={seed}: final items mismatch\n"
        f"  cache:  {sorted(cache.items())}\n"
        f"  shadow: {sorted(shadow.items())}"
    )


def test_shadow_model_standard():
    """High-volume shadow-model run with a balanced workload."""
    _run_shadow_comparison(
        seed=1234, capacity=8, n_ops=10_000,
        key_range=20, val_range=1000, write_prob=0.7
    )


def test_shadow_model_heavy_eviction():
    """Small capacity relative to key range forces frequent evictions."""
    _run_shadow_comparison(
        seed=42, capacity=3, n_ops=5_000,
        key_range=15, val_range=500, write_prob=0.6
    )


def test_shadow_model_heavy_reads():
    """Read-heavy workload: many misses expected."""
    _run_shadow_comparison(
        seed=99, capacity=10, n_ops=5_000,
        key_range=30, val_range=200, write_prob=0.3
    )


def test_shadow_model_capacity_one():
    """Capacity of 1: every put that changes the key must evict the previous."""
    _run_shadow_comparison(
        seed=7, capacity=1, n_ops=2_000,
        key_range=5, val_range=100, write_prob=0.6
    )


def test_shadow_model_large_capacity():
    """Capacity larger than key range: no evictions should occur."""
    _run_shadow_comparison(
        seed=555, capacity=50, n_ops=3_000,
        key_range=10, val_range=100, write_prob=0.5
    )


def test_shadow_model_value_none():
    """Stored values of None must be distinguishable from a cache miss."""
    rng = random.Random(321)
    capacity = 5
    cache = LruCache(capacity=capacity)
    shadow = ShadowLruCache(capacity=capacity)

    for step in range(2_000):
        k = rng.randrange(0, 10)
        if rng.random() < 0.6:
            # Sometimes store None as the value
            v = None if rng.random() < 0.3 else rng.randrange(0, 50)
            cache.put(k, v)
            shadow.put(k, v)
        else:
            result = cache.get(k)
            expected = shadow.get(k)
            assert result == expected, (
                f"step={step} get({k}): got {result!r}, expected {expected!r}"
            )

    assert sorted(cache.items()) == sorted(shadow.items())


# ---------------------------------------------------------------------------
# Targeted behavioural / contract tests
# ---------------------------------------------------------------------------

def test_get_miss_returns_none():
    cache = LruCache(capacity=4)
    assert cache.get("missing") is None


def test_put_and_get_basic():
    cache = LruCache(capacity=4)
    cache.put("a", 1)
    assert cache.get("a") == 1


def test_put_updates_existing_key():
    cache = LruCache(capacity=4)
    cache.put("x", 10)
    cache.put("x", 20)
    assert cache.get("x") == 20
    assert len(cache) == 1


def test_len_empty():
    cache = LruCache(capacity=5)
    assert len(cache) == 0


def test_len_after_puts():
    cache = LruCache(capacity=5)
    cache.put(1, "a")
    cache.put(2, "b")
    cache.put(3, "c")
    assert len(cache) == 3


def test_len_does_not_exceed_capacity():
    capacity = 3
    cache = LruCache(capacity=capacity)
    for i in range(10):
        cache.put(i, i)
    assert len(cache) <= capacity


def test_eviction_removes_lru_entry():
    """After filling to capacity and inserting one more, the LRU key is gone."""
    cache = LruCache(capacity=3)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)
    # "a" is LRU; inserting "d" should evict "a"
    cache.put("d", 4)
    assert cache.get("a") is None
    assert cache.get("b") == 2
    assert cache.get("c") == 3
    assert cache.get("d") == 4


def test_get_promotes_to_most_recent():
    """Accessing a key moves it to MRU position so it is not evicted next."""
    cache = LruCache(capacity=3)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)
    # Access "a" — now "b" is the LRU
    cache.get("a")
    cache.put("d", 4)  # should evict "b", not "a"
    assert cache.get("b") is None
    assert cache.get("a") == 1
    assert cache.get("c") == 3
    assert cache.get("d") == 4


def test_put_existing_key_promotes_to_most_recent():
    """Re-putting an existing key should refresh its recency."""
    cache = LruCache(capacity=3)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)
    # Re-put "a" with a new value — it becomes MRU; "b" is now LRU
    cache.put("a", 99)
    cache.put("d", 4)  # should evict "b"
    assert cache.get("b") is None
    assert cache.get("a") == 99


def test_items_returns_all_held_pairs():
    cache = LruCache(capacity=5)
    cache.put("x", 10)
    cache.put("y", 20)
    cache.put("z", 30)
    assert sorted(cache.items()) == [("x", 10), ("y", 20), ("z", 30)]


def test_items_empty_cache():
    cache = LruCache(capacity=5)
    assert cache.items() == []


def test_items_reflects_evictions():
    cache = LruCache(capacity=2)
    cache.put(1, "one")
    cache.put(2, "two")
    cache.put(3, "three")  # evicts key 1
    result = dict(cache.items())
    assert 1 not in result
    assert result.get(2) == "two"
    assert result.get(3) == "three"


def test_items_count_matches_len():
    cache = LruCache(capacity=4)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)
    assert len(cache.items()) == len(cache)


def test_capacity_one_always_holds_last_written():
    cache = LruCache(capacity=1)
    for i in range(20):
        cache.put(i, i * 10)
    assert len(cache) == 1
    assert cache.get(19) == 190
    for i in range(19):
        assert cache.get(i) is None


def test_no_duplicate_keys_in_items():
    """items() must not return duplicates even after repeated puts."""
    cache = LruCache(capacity=5)
    for _ in range(10):
        cache.put("dup", 42)
    keys = [k for k, _ in cache.items()]
    assert keys.count("dup") == 1


def test_integer_and_string_keys_coexist():
    cache = LruCache(capacity=4)
    cache.put(1, "int-key")
    cache.put("1", "str-key")
    assert cache.get(1) == "int-key"
    assert cache.get("1") == "str-key"
    assert len(cache) == 2


def test_various_value_types():
    cache = LruCache(capacity=5)
    cache.put("list", [1, 2, 3])
    cache.put("dict", {"a": 1})
    cache.put("tuple", (4, 5))
    assert cache.get("list") == [1, 2, 3]
    assert cache.get("dict") == {"a": 1}
    assert cache.get("tuple") == (4, 5)


def test_full_then_all_read():
    """Read every key in reverse insertion order after filling to capacity;
    the cache contents must be stable (no eviction during reads)."""
    capacity = 5
    cache = LruCache(capacity=capacity)
    for i in range(capacity):
        cache.put(i, i * 2)
    for i in reversed(range(capacity)):
        assert cache.get(i) == i * 2
    assert len(cache) == capacity


def test_repeated_same_key_no_growth():
    cache = LruCache(capacity=3)
    for v in range(50):
        cache.put("same", v)
    assert len(cache) == 1
    assert cache.get("same") == 49


def test_shadow_model_alternating_seeds():
    """Run multiple independent shadow-model trials with distinct seeds to
    increase confidence across different random trajectories."""
    for seed in range(10):
        _run_shadow_comparison(
            seed=seed * 1000 + 7, capacity=6, n_ops=2_000,
            key_range=15, val_range=200, write_prob=0.65
        )
