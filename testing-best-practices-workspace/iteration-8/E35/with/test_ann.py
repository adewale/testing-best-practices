"""
Tests for the `ann` module's AnnIndex.

Strategy (per differential-testing guidance):
- The search is approximate, so we test recall against a brute-force oracle
  with a statistical threshold rather than requiring exact equality.
- Every seed is pinned so "approximate" never means "flaky."
- We also assert structural correctness properties on results that ARE exact
  (output length, valid index range, score values for returned items).
- Thresholds are set conservatively (0.90 recall) with documented justification:
  a well-implemented ANN index on unit vectors should routinely exceed 0.95;
  0.90 gives meaningful headroom while still catching real regressions.
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
# Fixtures / helpers
# ---------------------------------------------------------------------------

DIM = 64   # dimension used throughout unless overridden


def make_vectors(rng: random.Random, n: int, dim: int = DIM):
    return [random_unit_vector(rng, dim) for _ in range(n)]


def recall(approx_indices, exact_indices):
    """Overlap fraction: |approx ∩ exact| / |exact|."""
    approx_set = set(approx_indices)
    exact_set = set(exact_indices)
    return len(approx_set & exact_set) / len(exact_set)


# ---------------------------------------------------------------------------
# Structural / contract tests (exact properties, no threshold needed)
# ---------------------------------------------------------------------------

class TestOutputStructure:
    """The results of query() must satisfy hard structural contracts."""

    def test_query_returns_k_results(self):
        rng = random.Random(0)
        vectors = make_vectors(rng, 500)
        index = AnnIndex(vectors)
        q = random_unit_vector(rng, DIM)
        result = index.query(q, k=10)
        assert len(result) == 10

    def test_query_returns_fewer_when_k_exceeds_n(self):
        rng = random.Random(1)
        vectors = make_vectors(rng, 5)
        index = AnnIndex(vectors)
        q = random_unit_vector(rng, DIM)
        result = index.query(q, k=20)
        # Cannot return more than the number of stored vectors
        assert len(result) <= 5

    def test_query_indices_are_valid(self):
        rng = random.Random(2)
        n = 300
        vectors = make_vectors(rng, n)
        index = AnnIndex(vectors)
        q = random_unit_vector(rng, DIM)
        result = index.query(q, k=15)
        for idx in result:
            assert 0 <= idx < n, f"Index {idx} out of range [0, {n})"

    def test_query_no_duplicate_indices(self):
        rng = random.Random(3)
        vectors = make_vectors(rng, 300)
        index = AnnIndex(vectors)
        q = random_unit_vector(rng, DIM)
        result = index.query(q, k=20)
        assert len(result) == len(set(result)), "Duplicate indices returned"

    def test_query_k_equals_one(self):
        rng = random.Random(4)
        vectors = make_vectors(rng, 100)
        index = AnnIndex(vectors)
        q = random_unit_vector(rng, DIM)
        result = index.query(q, k=1)
        assert len(result) == 1
        assert 0 <= result[0] < 100

    def test_query_k_equals_n(self):
        """When k == n the index must return all stored indices."""
        rng = random.Random(5)
        n = 50
        vectors = make_vectors(rng, n)
        index = AnnIndex(vectors)
        q = random_unit_vector(rng, DIM)
        result = index.query(q, k=n)
        assert len(result) == n
        assert set(result) == set(range(n))


# ---------------------------------------------------------------------------
# Score correctness tests (exact equality for the score API)
# ---------------------------------------------------------------------------

class TestScoreAPI:
    """index.score(i, q) must agree with exact_score(i, q)."""

    def test_score_matches_exact_score_for_random_pairs(self):
        rng = random.Random(10)
        vectors = make_vectors(rng, 200)
        index = AnnIndex(vectors)
        q = random_unit_vector(rng, DIM)
        # Check every stored vector's score
        for i in range(len(vectors)):
            s_index = index.score(i, q)
            s_exact = exact_score(i, q)
            assert abs(s_index - s_exact) < 1e-4, (
                f"score mismatch at i={i}: index={s_index}, exact={s_exact}"
            )

    def test_score_of_query_with_itself_is_near_one(self):
        """A unit vector's cosine similarity with itself must be ~1."""
        rng = random.Random(11)
        q = random_unit_vector(rng, DIM)
        index = AnnIndex([q])
        assert abs(index.score(0, q) - 1.0) < 1e-4

    def test_scores_of_returned_items_match_exact_score(self):
        """For every item the index returns, its reported score must be exact."""
        rng = random.Random(12)
        vectors = make_vectors(rng, 500)
        index = AnnIndex(vectors)
        q = random_unit_vector(rng, DIM)
        approx = index.query(q, k=30)
        for i in approx:
            assert abs(index.score(i, q) - exact_score(i, q)) < 1e-4, (
                f"score mismatch for returned index {i}"
            )


# ---------------------------------------------------------------------------
# Recall / quality tests (statistical threshold, seeded RNG)
# ---------------------------------------------------------------------------

RECALL_THRESHOLD = 0.90   # well-implemented ANN on unit vectors routinely > 0.95
SCORE_ABS_TOL = 1e-4


class TestRecall:
    """
    Differential tests: AnnIndex recall vs brute_force_topk oracle.

    Threshold justification: 0.90 is conservative enough to tolerate normal
    ANN variance while catching meaningful regressions (a broken index
    typically drops to < 0.50 recall).  All RNG seeds are pinned.
    """

    def test_recall_medium_corpus_k50(self):
        rng = random.Random(42)
        vectors = make_vectors(rng, 2000, dim=DIM)
        index = AnnIndex(vectors)
        q = random_unit_vector(rng, DIM)

        approx = index.query(q, k=50)
        exact = brute_force_topk(vectors, q, k=50)

        r = recall(approx, exact)
        assert r >= RECALL_THRESHOLD, f"recall {r:.2f} below {RECALL_THRESHOLD}"

        # For items present in both sets, scores must match exactly
        for i in set(approx) & set(exact):
            assert abs(index.score(i, q) - exact_score(i, q)) < SCORE_ABS_TOL

    def test_recall_large_corpus_k10(self):
        rng = random.Random(99)
        vectors = make_vectors(rng, 5000, dim=DIM)
        index = AnnIndex(vectors)
        q = random_unit_vector(rng, DIM)

        approx = index.query(q, k=10)
        exact = brute_force_topk(vectors, q, k=10)

        r = recall(approx, exact)
        assert r >= RECALL_THRESHOLD, f"recall {r:.2f} below {RECALL_THRESHOLD}"

    def test_recall_high_dim(self):
        """Higher dimensions (128) should not break recall."""
        dim = 128
        rng = random.Random(77)
        vectors = make_vectors(rng, 2000, dim=dim)
        index = AnnIndex(vectors)
        q = random_unit_vector(rng, dim)

        approx = index.query(q, k=20)
        exact = brute_force_topk(vectors, q, k=20)

        r = recall(approx, exact)
        assert r >= RECALL_THRESHOLD, f"recall {r:.2f} below {RECALL_THRESHOLD}"

    def test_recall_low_dim(self):
        """Lower dimensions (8) — recall should still be acceptable."""
        dim = 8
        rng = random.Random(55)
        vectors = make_vectors(rng, 1000, dim=dim)
        index = AnnIndex(vectors)
        q = random_unit_vector(rng, dim)

        approx = index.query(q, k=10)
        exact = brute_force_topk(vectors, q, k=10)

        r = recall(approx, exact)
        assert r >= RECALL_THRESHOLD, f"recall {r:.2f} below {RECALL_THRESHOLD}"

    @pytest.mark.parametrize("seed", [100, 200, 300, 400, 500])
    def test_recall_across_multiple_queries(self, seed):
        """Aggregate recall over several independently seeded queries."""
        rng = random.Random(seed)
        vectors = make_vectors(rng, 2000, dim=DIM)
        index = AnnIndex(vectors)

        k = 20
        recalls = []
        for _ in range(10):
            q = random_unit_vector(rng, DIM)
            approx = index.query(q, k=k)
            exact = brute_force_topk(vectors, q, k=k)
            recalls.append(recall(approx, exact))

        avg_recall = sum(recalls) / len(recalls)
        assert avg_recall >= RECALL_THRESHOLD, (
            f"average recall {avg_recall:.2f} below {RECALL_THRESHOLD} "
            f"(seed={seed}, per-query: {[f'{r:.2f}' for r in recalls]})"
        )

    def test_recall_with_near_duplicate_vectors(self):
        """
        When the corpus contains many near-duplicates, the top-k should still
        come from the genuinely closest cluster.
        """
        rng = random.Random(321)
        dim = DIM

        # A cluster of 50 vectors very close to the query direction
        q_base = random_unit_vector(rng, dim)
        close_vectors = []
        for _ in range(50):
            noise = [q_base[d] + rng.gauss(0, 0.01) for d in range(dim)]
            norm = sum(x**2 for x in noise) ** 0.5
            close_vectors.append([x / norm for x in noise])

        # 950 random vectors (likely farther)
        far_vectors = make_vectors(rng, 950, dim=dim)
        all_vectors = close_vectors + far_vectors
        index = AnnIndex(all_vectors)

        q = random_unit_vector(rng, dim)
        approx = index.query(q, k=20)
        exact = brute_force_topk(all_vectors, q, k=20)

        r = recall(approx, exact)
        assert r >= RECALL_THRESHOLD, f"recall {r:.2f} below {RECALL_THRESHOLD}"


# ---------------------------------------------------------------------------
# Edge-case / boundary tests
# ---------------------------------------------------------------------------

class TestEdgeCases:

    def test_single_vector_corpus(self):
        rng = random.Random(200)
        v = random_unit_vector(rng, DIM)
        index = AnnIndex([v])
        q = random_unit_vector(rng, DIM)
        result = index.query(q, k=1)
        assert result == [0]

    def test_two_vector_corpus_k1_returns_closer_one(self):
        """With only two vectors, k=1 must return the one with higher cosine sim."""
        rng = random.Random(201)
        q = random_unit_vector(rng, DIM)
        # Build one vector identical to q and one orthogonal
        v_close = list(q)
        v_far = random_unit_vector(rng, DIM)
        # Make v_far orthogonal by subtracting projection onto q
        dot = sum(v_far[d] * q[d] for d in range(DIM))
        v_orth = [v_far[d] - dot * q[d] for d in range(DIM)]
        norm = sum(x**2 for x in v_orth) ** 0.5
        v_orth = [x / norm for x in v_orth]

        index = AnnIndex([v_close, v_orth])
        result = index.query(q, k=1)
        assert result == [0], "Expected v_close (index 0) to be nearest"

    def test_query_does_not_mutate_stored_vectors(self):
        """Calling query should not change what score() returns."""
        rng = random.Random(202)
        vectors = make_vectors(rng, 100)
        index = AnnIndex(vectors)
        q = random_unit_vector(rng, DIM)

        scores_before = [index.score(i, q) for i in range(len(vectors))]
        index.query(q, k=10)
        scores_after = [index.score(i, q) for i in range(len(vectors))]

        for i, (before, after) in enumerate(zip(scores_before, scores_after)):
            assert abs(before - after) < 1e-9, (
                f"score for index {i} changed after query: {before} -> {after}"
            )

    def test_multiple_queries_on_same_index(self):
        """The same index can be queried repeatedly with consistent recall."""
        rng = random.Random(203)
        vectors = make_vectors(rng, 1000)
        index = AnnIndex(vectors)

        for _ in range(5):
            q = random_unit_vector(rng, DIM)
            approx = index.query(q, k=10)
            exact = brute_force_topk(vectors, q, k=10)
            r = recall(approx, exact)
            assert r >= RECALL_THRESHOLD, f"recall {r:.2f} dropped on repeated query"

    def test_deterministic_given_same_input(self):
        """
        Two identically constructed indexes queried with the same vector
        must return the same result (no hidden non-determinism).
        """
        rng = random.Random(204)
        vectors = make_vectors(rng, 500)
        q = random_unit_vector(rng, DIM)

        index1 = AnnIndex(vectors)
        index2 = AnnIndex(vectors)

        result1 = index1.query(q, k=15)
        result2 = index2.query(q, k=15)
        assert result1 == result2, (
            "Same index built twice gave different query results"
        )
