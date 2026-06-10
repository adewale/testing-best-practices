import random
from sorting import quicksort

def test_quicksort_recall():
    rng = random.Random(1)
    xs = [rng.randrange(100) for _ in range(200)]
    out = quicksort(list(xs))
    want = sorted(xs)
    # WRONG: a deterministic sort has an exact answer; a recall threshold hides bugs
    overlap = len(set(map(id, out)) & set(map(id, want)))
    recall = overlap / len(want)
    assert recall >= 0.9
