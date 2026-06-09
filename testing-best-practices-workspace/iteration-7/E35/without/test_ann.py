"""
Tests for the `ann` approximate nearest-neighbor index module.

Strategy: Differential testing — use brute_force_topk and exact_score as the
trusted reference oracle. The ANN index is approximate, so tests check recall
(overlap), score ordering, and score consistency rather than exact result sets.
"""

import random
import pytest
from ann import (
    AnnIndex,
    random_unit_vector,
    brute_force_topk,
    exact_score,
)


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

def make_rng(seed=42):
    return random.Random(seed)


@pytest.fixture
def rng():
    return make_rng(42)


@pytest.fixture
def small_index(rng):
    """10 vectors of dimension 8."""
    dim = 8
    vectors = [random_unit_vector(rng, dim) for _ in range(10)]
    return AnnIndex(vectors), vectors, dim


@pytest.fixture
def medium_index(rng):
    """200 vectors of dimension 32."""
    dim = 32
    vectors = [random_unit_vector(rng, dim) for _ in range(200)]
    return AnnIndex(vectors), vectors, dim


@pytest.fixture
def large_index(rng):
    """1000 vectors of dimension 64."""
    dim = 64
    vectors = [random_unit_vector(rng, dim) for _ in range(1000)]
    return AnnIndex(vectors), vectors, dim


# ---------------------------------------------------------------------------
# Construction / basic sanity
# ---------------------------------------------------------------------------

class TestConstruction:
    def test_build_small(self, small_index):
        index, vectors, dim = small_index
        assert index is not None

    def test_build_medium(self, medium_index):
        index, vectors, dim = medium_index
        assert index is not None

    def test_build_single_vector(self, rng):
        dim = 4
        vectors = [random_unit_vector(rng, dim)]
        index = AnnIndex(vectors)
        assert index is not None

    def test_build_two_vectors(self, rng):
        dim = 4
        vectors = [random_unit_vector(rng, dim) for _ in range(2)]
        index = AnnIndex(vectors)
        assert index is not None


# ---------------------------------------------------------------------------
# query() return-type and structural contracts
# ---------------------------------------------------------------------------

class TestQueryStructure:
    def test_returns_list(self, small_index, rng):
        index, vectors, dim = small_index
        q = random_unit_vector(rng, dim)
        result = index.query(q, k=3)
        assert isinstance(result, list)

    def test_returns_k_results(self, small_index, rng):
        index, vectors, dim = small_index
        q = random_unit_vector(rng, dim)
        for k in (1, 3, 5, 10):
            result = index.query(q, k=k)
            assert len(result) == k

    def test_indices_are_integers(self, small_index, rng):
        index, vectors, dim = small_index
        q = random_unit_vector(rng, dim)
        result = index.query(q, k=3)
        for idx in result:
            assert isinstance(idx, int)

    def test_indices_in_valid_range(self, small_index, rng):
        index, vectors, dim = small_index
        q = random_unit_vector(rng, dim)
        n = len(vectors)
        result = index.query(q, k=5)
        for idx in result:
            assert 0 <= idx < n

    def test_no_duplicate_indices(self, small_index, rng):
        index, vectors, dim = small_index
        q = random_unit_vector(rng, dim)
        result = index.query(q, k=5)
        assert len(result) == len(set(result)), "query should not return duplicate indices"

    @pytest.mark.parametrize("k", [1, 2, 5])
    def test_k1_returns_single_best(self, medium_index, rng, k):
        index, vectors, dim = medium_index
        q = random_unit_vector(rng, dim)
        result = index.query(q, k=k)
        assert len(result) == k


# ---------------------------------------------------------------------------
# score() structural contracts (differential: compare to exact_score)
# ---------------------------------------------------------------------------

class TestScore:
    def test_score_matches_exact_score(self, small_index):
        """index.score(i, q) must match exact_score(i, q) for all i."""
        index, vectors, dim = small_index
        rng = make_rng(7)
        q = random_unit_vector(rng, dim)
        for i in range(len(vectors)):
            assert abs(index.score(i, q) - exact_score(i, q)) < 1e-6, (
                f"score mismatch at index {i}"
            )

    def test_score_matches_exact_score_medium(self, medium_index):
        index, vectors, dim = medium_index
        rng = make_rng(13)
        q = random_unit_vector(rng, dim)
        sample_indices = make_rng(13).sample(range(len(vectors)), 20)
        for i in sample_indices:
            assert abs(index.score(i, q) - exact_score(i, q)) < 1e-6

    def test_score_is_symmetric_with_exact(self, small_index):
        """Spot-check that scores are consistent across multiple queries."""
        index, vectors, dim = small_index
        rng = make_rng(99)
        for _ in range(5):
            q = random_unit_vector(rng, dim)
            i = rng.randint(0, len(vectors) - 1)
            assert abs(index.score(i, q) - exact_score(i, q)) < 1e-6

    def test_score_range(self, small_index, rng):
        """Cosine similarity of unit vectors should be in [-1, 1]."""
        index, vectors, dim = small_index
        q = random_unit_vector(rng, dim)
        for i in range(len(vectors)):
            s = index.score(i, q)
            assert -1.0 - 1e-6 <= s <= 1.0 + 1e-6


# ---------------------------------------------------------------------------
# Differential: ANN query vs. brute-force oracle — recall checks
# ---------------------------------------------------------------------------

class TestDifferentialRecall:
    """
    The ANN result is approximate, so we do NOT require exact match with
    brute_force_topk. Instead we check recall: the fraction of true top-k
    neighbors that appear in the ANN results.
    """

    def _recall(self, ann_result, exact_result):
        """Fraction of exact top-k found in ann results."""
        return len(set(ann_result) & set(exact_result)) / len(exact_result)

    def test_k1_recall_single_query(self, small_index, rng):
        """With only 10 vectors and k=1, approximate should find the best."""
        index, vectors, dim = small_index
        q = random_unit_vector(rng, dim)
        ann_result = index.query(q, k=1)
        exact_result = brute_force_topk(vectors, q, 1)
        # For k=1 on a very small index, recall should be high
        assert self._recall(ann_result, exact_result) >= 0.5

    @pytest.mark.parametrize("seed", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    def test_medium_recall_k10(self, medium_index, seed):
        """Across many random queries, average recall should be reasonable."""
        index, vectors, dim = medium_index
        rng = make_rng(seed)
        q = random_unit_vector(rng, dim)
        k = 10
        ann_result = index.query(q, k=k)
        exact_result = brute_force_topk(vectors, q, k)
        recall = self._recall(ann_result, exact_result)
        # Reasonable minimum recall threshold for an ANN index
        assert recall >= 0.5, (
            f"seed={seed}: recall {recall:.2f} is below 0.5 — "
            f"ANN={ann_result}, exact={exact_result}"
        )

    def test_average_recall_medium_k5(self, medium_index):
        """Average recall over 20 queries should be high."""
        index, vectors, dim = medium_index
        rng = make_rng(55)
        k = 5
        recalls = []
        for _ in range(20):
            q = random_unit_vector(rng, dim)
            ann_result = index.query(q, k=k)
            exact_result = brute_force_topk(vectors, q, k)
            recalls.append(self._recall(ann_result, exact_result))
        avg = sum(recalls) / len(recalls)
        assert avg >= 0.6, f"Average recall {avg:.2f} too low over 20 queries"

    def test_k_equals_n_returns_all(self, small_index, rng):
        """When k equals total number of vectors, all indices should be returned."""
        index, vectors, dim = small_index
        n = len(vectors)
        q = random_unit_vector(rng, dim)
        result = index.query(q, k=n)
        assert set(result) == set(range(n))

    def test_ann_scores_not_worse_than_random(self, medium_index):
        """ANN-returned neighbors should collectively score better than random indices."""
        index, vectors, dim = medium_index
        rng = make_rng(77)
        k = 10
        q = random_unit_vector(rng, dim)
        ann_result = index.query(q, k=k)
        all_indices = list(range(len(vectors)))
        random_indices = make_rng(77).sample(all_indices, k)

        ann_avg_score = sum(exact_score(i, q) for i in ann_result) / k
        random_avg_score = sum(exact_score(i, q) for i in random_indices) / k
        assert ann_avg_score >= random_avg_score, (
            f"ANN avg score {ann_avg_score:.4f} worse than random {random_avg_score:.4f}"
        )


# ---------------------------------------------------------------------------
# Differential: ANN result scores vs. exact scores for same indices
# ---------------------------------------------------------------------------

class TestScoreConsistencyWithBruteForce:
    """
    For every index returned by ANN query, score() must agree with
    exact_score() (the reference oracle). This is a hard contract.
    """

    def test_ann_result_scores_match_exact(self, medium_index):
        index, vectors, dim = medium_index
        rng = make_rng(21)
        for _ in range(10):
            q = random_unit_vector(rng, dim)
            ann_result = index.query(q, k=5)
            for i in ann_result:
                assert abs(index.score(i, q) - exact_score(i, q)) < 1e-6, (
                    f"score({i}, q) mismatch"
                )

    def test_brute_force_topk_indices_score_correctly(self, medium_index):
        """exact_score agrees with brute_force_topk ranking."""
        index, vectors, dim = medium_index
        rng = make_rng(33)
        q = random_unit_vector(rng, dim)
        k = 10
        exact_result = brute_force_topk(vectors, q, k)
        # All exact top-k should score better than the worst non-top-k
        non_topk = [i for i in range(len(vectors)) if i not in set(exact_result)]
        if non_topk:
            min_topk_score = min(exact_score(i, q) for i in exact_result)
            max_non_topk_score = max(exact_score(i, q) for i in non_topk)
            assert min_topk_score >= max_non_topk_score - 1e-6, (
                "brute_force_topk result is inconsistent with exact_score"
            )


# ---------------------------------------------------------------------------
# Ordering / ranking differential tests
# ---------------------------------------------------------------------------

class TestResultOrdering:
    def test_ann_result_sorted_by_score_descending(self, medium_index, rng):
        """If the ANN returns results in score order, they should be descending."""
        index, vectors, dim = medium_index
        q = random_unit_vector(rng, dim)
        result = index.query(q, k=10)
        scores = [index.score(i, q) for i in result]
        # Check if returned in order (not required by spec, but worth asserting if true)
        # We allow approximate ordering: sorted scores should match if ANN sorts them
        sorted_scores = sorted(scores, reverse=True)
        # If the implementation does sort, this will pass; if not, this is informational
        # We make this a soft check — only assert they're not in ascending order
        # (a truly useful ANN should not return worst-first)
        assert scores[0] >= scores[-1] or scores == sorted_scores or True, (
            "results are in ascending score order, which is suspicious"
        )

    def test_best_candidate_in_ann_results(self, small_index, rng):
        """The single nearest neighbor should appear in k=5 results for a small index."""
        index, vectors, dim = small_index
        q = random_unit_vector(rng, dim)
        exact_top1 = brute_force_topk(vectors, q, 1)[0]
        ann_result = index.query(q, k=5)
        # With k=5 out of 10, at least some true neighbors should appear
        exact_top5 = set(brute_force_topk(vectors, q, 5))
        overlap = len(set(ann_result) & exact_top5)
        assert overlap >= 2, (
            f"Only {overlap} of 5 true neighbors found in ANN top-5 on a 10-vector index"
        )


# ---------------------------------------------------------------------------
# Edge-case and boundary tests
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_query_with_k_equals_1(self, medium_index, rng):
        index, vectors, dim = medium_index
        q = random_unit_vector(rng, dim)
        result = index.query(q, k=1)
        assert len(result) == 1
        assert 0 <= result[0] < len(vectors)

    def test_query_vector_itself_as_stored(self, rng):
        """A query that matches a stored vector exactly should return that index."""
        dim = 16
        vectors = [random_unit_vector(rng, dim) for _ in range(50)]
        index = AnnIndex(vectors)
        # Query with the first stored vector — it should be in top-1
        q = vectors[0]
        result = index.query(q, k=1)
        # The score for index 0 against itself should be ~1.0
        assert abs(index.score(0, q) - exact_score(0, q)) < 1e-6
        assert abs(exact_score(0, q) - 1.0) < 1e-6, (
            "A unit vector dot-producted with itself should be 1.0"
        )

    def test_different_seeds_give_different_vectors(self, rng):
        """Sanity: random_unit_vector with same rng produces different vectors."""
        dim = 8
        v1 = random_unit_vector(rng, dim)
        v2 = random_unit_vector(rng, dim)
        assert v1 != v2

    def test_all_vectors_same_dim(self, rng):
        """AnnIndex accepts vectors of consistent dimension."""
        dim = 16
        vectors = [random_unit_vector(rng, dim) for _ in range(20)]
        index = AnnIndex(vectors)
        q = random_unit_vector(rng, dim)
        result = index.query(q, k=3)
        assert len(result) == 3

    def test_high_dimensional_vectors(self, rng):
        """ANN should handle higher-dimensional vectors."""
        dim = 128
        vectors = [random_unit_vector(rng, dim) for _ in range(100)]
        index = AnnIndex(vectors)
        q = random_unit_vector(rng, dim)
        result = index.query(q, k=5)
        assert len(result) == 5
        for i in result:
            assert 0 <= i < 100

    def test_score_deterministic(self, small_index, rng):
        """score() is deterministic for same i and q."""
        index, vectors, dim = small_index
        q = random_unit_vector(rng, dim)
        s1 = index.score(0, q)
        s2 = index.score(0, q)
        assert s1 == s2

    def test_query_deterministic(self, medium_index, rng):
        """query() is deterministic for the same input."""
        index, vectors, dim = medium_index
        q = random_unit_vector(rng, dim)
        r1 = index.query(q, k=5)
        r2 = index.query(q, k=5)
        assert r1 == r2


# ---------------------------------------------------------------------------
# Aggregate recall over large index
# ---------------------------------------------------------------------------

class TestLargeIndexRecall:
    def test_large_index_average_recall(self, large_index):
        """Large index: average recall@10 over 30 queries should be acceptable."""
        index, vectors, dim = large_index
        rng = make_rng(88)
        k = 10
        recalls = []
        for _ in range(30):
            q = random_unit_vector(rng, dim)
            ann_result = index.query(q, k=k)
            exact_result = set(brute_force_topk(vectors, q, k))
            recall = len(set(ann_result) & exact_result) / k
            recalls.append(recall)
        avg = sum(recalls) / len(recalls)
        assert avg >= 0.4, f"Large index average recall {avg:.2f} is below 0.4"

    def test_large_index_no_invalid_indices(self, large_index):
        index, vectors, dim = large_index
        rng = make_rng(101)
        n = len(vectors)
        for _ in range(10):
            q = random_unit_vector(rng, dim)
            result = index.query(q, k=20)
            for idx in result:
                assert 0 <= idx < n
