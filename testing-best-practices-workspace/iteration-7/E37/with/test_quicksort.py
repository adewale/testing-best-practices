import pytest
import random

from sorting import quicksort

# ---------------------------------------------------------------------------
# Test cases: (label, input_list)
# The oracle is Python's built-in sorted() — no hand-written expected values.
# ---------------------------------------------------------------------------

_CASES = [
    ("empty",              []),
    ("single",             [42]),
    ("two_sorted",         [1, 2]),
    ("two_reversed",       [2, 1]),
    ("already_sorted",     [1, 2, 3, 4, 5]),
    ("reverse_sorted",     [5, 4, 3, 2, 1]),
    ("all_equal",          [7, 7, 7, 7]),
    ("duplicates_mixed",   [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]),
    ("negative_values",    [-3, -1, -7, -2, 0]),
    ("mixed_sign",         [3, -2, 0, 7, -5, 1]),
    ("single_duplicate",   [2, 2]),
    ("large_range",        list(range(100, 0, -1))),
]


@pytest.mark.parametrize("label,xs", _CASES, ids=[c[0] for c in _CASES])
def test_matches_sorted_builtin(label, xs):
    """quicksort output must equal sorted() for every test input."""
    assert quicksort(xs) == sorted(xs)


# ---------------------------------------------------------------------------
# Seeded random inputs — differential against sorted() at scale.
# Seed is pinned so failures are reproducible.
# ---------------------------------------------------------------------------

def _random_cases(seed: int, count: int, max_len: int, value_range: tuple):
    rng = random.Random(seed)
    cases = []
    for _ in range(count):
        length = rng.randint(0, max_len)
        lst = [rng.randint(*value_range) for _ in range(length)]
        cases.append(lst)
    return cases


_RANDOM_CASES = _random_cases(seed=20240601, count=200, max_len=300, value_range=(-1000, 1000))


@pytest.mark.parametrize("xs", _RANDOM_CASES)
def test_matches_sorted_builtin_random(xs):
    """quicksort output must equal sorted() across 200 seeded random lists."""
    assert quicksort(xs) == sorted(xs)


# ---------------------------------------------------------------------------
# Structural / contract tests
# ---------------------------------------------------------------------------

def test_returns_new_list():
    """quicksort must return a new list, not mutate the original."""
    original = [3, 1, 2]
    copy = list(original)
    result = quicksort(original)
    assert original == copy, "input list was mutated"
    assert result is not original, "returned the same list object"


def test_preserves_length():
    """Output length must equal input length (no elements lost or duplicated)."""
    xs = [5, 3, 8, 1, 9, 2, 4, 7, 6]
    assert len(quicksort(xs)) == len(xs)


def test_preserves_element_multiset():
    """Output must contain exactly the same elements (counts) as input."""
    xs = [4, 2, 7, 2, 4, 4, 1]
    from collections import Counter
    assert Counter(quicksort(xs)) == Counter(xs)
