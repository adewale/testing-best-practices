import random
from sorting import quicksort

def test_matches_builtin_sorted():
    assert quicksort([3, 1, 2]) == [1, 2, 3]
    assert quicksort([]) == []
    assert quicksort([5, 5, 1]) == [1, 5, 5]

def test_is_permutation_and_ordered():
    rng = random.Random(1)
    xs = [rng.randrange(100) for _ in range(200)]
    out = quicksort(list(xs))
    assert out == sorted(xs)                       # exact, deterministic
    assert sorted(out) == sorted(xs)               # permutation preserved
