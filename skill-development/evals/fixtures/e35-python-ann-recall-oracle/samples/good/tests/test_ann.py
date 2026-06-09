import random
from ann import AnnIndex, random_unit_vector, brute_force_topk, exact_score

def test_recall_against_brute_force():
    rng = random.Random(42)
    vectors = [random_unit_vector(rng, dim=128) for _ in range(20000)]
    index = AnnIndex(vectors)
    query = random_unit_vector(rng, dim=128)

    approx = set(index.query(query, k=50))
    exact = set(brute_force_topk(vectors, query, k=50))   # the oracle

    recall = len(approx & exact) / 50
    assert recall >= 0.90, f"recall {recall:.2f} below 0.90 threshold"
    for item in approx & exact:                            # exact on the overlap
        assert abs(index.score(item, query) - exact_score(item, query)) < 1e-4
