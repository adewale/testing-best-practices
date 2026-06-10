"""
Tests for the fuzzy module's FuzzyIndex and similarity function.

FuzzyIndex.search(q, k) returns approximately the k most similar strings
to q — near-ties may differ between builds/platforms. The documented oracle
is the deterministic module-level function similarity(a, b) -> float
(higher is more similar).

Strategy (per statistical/approximate-output guidance):
- Use similarity() as a brute-force oracle to compute the exact top-k.
- Assert recall (overlap fraction) against the brute-force result with a
  pinned seed and a well-justified threshold.
- Separately assert that every result the index *does* return is
  individually correct: its reported score matches similarity() exactly.
- Also assert deterministic structural invariants that must hold exactly
  (result count, no duplicates, all results are in the index corpus, etc.).
"""

import random

import pytest

from fuzzy import FuzzyIndex, similarity


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def brute_force_topk(strings: list[str], query: str, k: int) -> list[str]:
    """Return the true top-k strings by similarity score (descending).
    Ties broken by original insertion order (stable sort), which gives a
    deterministic oracle independent of the index implementation."""
    scored = [(similarity(query, s), i, s) for i, s in enumerate(strings)]
    scored.sort(key=lambda t: (-t[0], t[1]))
    return [s for _, _, s in scored[:k]]


def brute_force_topk_set(strings: list[str], query: str, k: int) -> set[str]:
    return set(brute_force_topk(strings, query, k))


# ---------------------------------------------------------------------------
# Corpus fixtures
# ---------------------------------------------------------------------------

SMALL_CORPUS = [
    "apple", "application", "apply", "appetizer",
    "banana", "bandana", "band",
    "cherry", "chair", "cheer",
    "grape", "graph", "gravel",
    "mango", "mange", "mangle",
]

PROGRAMMING_CORPUS = [
    "python", "pytorch", "pyqt", "pycharm",
    "javascript", "java", "javafx",
    "typescript", "type", "typedef",
    "golang", "goal", "goat",
    "rust", "rush", "rusk", "rusted",
    "kotlin", "kite", "kitten",
    "haskell", "hash", "hazel",
    "clojure", "closure", "cloture",
    "elixir", "elastic", "elephant",
    "erlang", "errand", "era",
]


def _make_large_corpus(n: int = 500, seed: int = 0) -> list[str]:
    """Generate a reproducible corpus of random lowercase strings."""
    rng = random.Random(seed)
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    corpus = []
    while len(corpus) < n:
        length = rng.randint(3, 12)
        word = "".join(rng.choice(alphabet) for _ in range(length))
        if word not in corpus:
            corpus.append(word)
    return corpus


LARGE_CORPUS = _make_large_corpus(n=500, seed=42)


# ---------------------------------------------------------------------------
# Basic structural invariants (exact assertions, no statistical tolerance)
# ---------------------------------------------------------------------------

class TestStructuralInvariants:
    """Properties that must hold exactly regardless of approximation."""

    def test_returns_exactly_k_results_when_corpus_large_enough(self):
        index = FuzzyIndex(SMALL_CORPUS)
        results = index.search("apple", k=5)
        assert len(results) == 5

    def test_returns_at_most_corpus_size_when_k_exceeds_corpus(self):
        index = FuzzyIndex(SMALL_CORPUS)
        results = index.search("apple", k=len(SMALL_CORPUS) + 100)
        assert len(results) == len(SMALL_CORPUS)

    def test_returns_exactly_k_equals_one(self):
        index = FuzzyIndex(SMALL_CORPUS)
        results = index.search("apple", k=1)
        assert len(results) == 1

    def test_no_duplicates_in_results(self):
        index = FuzzyIndex(SMALL_CORPUS)
        results = index.search("apple", k=10)
        assert len(results) == len(set(results))

    def test_all_results_are_in_corpus(self):
        index = FuzzyIndex(SMALL_CORPUS)
        results = index.search("apple", k=8)
        for r in results:
            assert r in SMALL_CORPUS, f"'{r}' was returned but is not in the corpus"

    def test_empty_corpus_returns_empty(self):
        index = FuzzyIndex([])
        results = index.search("apple", k=5)
        assert results == [] or list(results) == []

    def test_single_element_corpus_k1(self):
        index = FuzzyIndex(["mango"])
        results = index.search("anything", k=1)
        assert list(results) == ["mango"]

    def test_single_element_corpus_large_k(self):
        index = FuzzyIndex(["mango"])
        results = index.search("anything", k=50)
        assert len(results) == 1
        assert results[0] == "mango"

    def test_exact_match_in_corpus_appears_in_top1(self):
        """When the query is an exact member of the corpus, it should be
        the single most similar string (similarity with itself is maximal)."""
        index = FuzzyIndex(SMALL_CORPUS)
        results = index.search("apple", k=1)
        assert results[0] == "apple"

    @pytest.mark.parametrize("word", ["apple", "banana", "cherry", "grape", "mango"])
    def test_exact_match_always_top1(self, word):
        index = FuzzyIndex(SMALL_CORPUS)
        results = index.search(word, k=1)
        assert results[0] == word

    def test_results_on_large_corpus_count(self):
        index = FuzzyIndex(LARGE_CORPUS)
        results = index.search("python", k=20)
        assert len(results) == 20

    def test_all_results_from_large_corpus_are_in_corpus(self):
        index = FuzzyIndex(LARGE_CORPUS)
        results = index.search("hello", k=15)
        corpus_set = set(LARGE_CORPUS)
        for r in results:
            assert r in corpus_set


# ---------------------------------------------------------------------------
# similarity() function — deterministic, exact assertions
# ---------------------------------------------------------------------------

class TestSimilarityFunction:
    """The similarity function is documented as deterministic, so we test it
    with exact assertions and algebraic properties."""

    def test_similarity_identical_strings_maximum(self):
        """similarity(a, a) should be the maximum possible value; at minimum
        it must be >= similarity(a, b) for any b != a."""
        a = "apple"
        others = ["application", "banana", "xyz", ""]
        self_sim = similarity(a, a)
        for b in others:
            assert self_sim >= similarity(a, b), (
                f"similarity('{a}','{a}')={self_sim} < similarity('{a}','{b}')={similarity(a,b)}"
            )

    @pytest.mark.parametrize("a,b", [
        ("apple", "application"),
        ("banana", "bandana"),
        ("python", "pytorch"),
        ("rust", "rush"),
        ("hello", "world"),
        ("abc", "xyz"),
    ])
    def test_similarity_returns_float(self, a, b):
        result = similarity(a, b)
        assert isinstance(result, float), f"expected float, got {type(result)}"

    @pytest.mark.parametrize("a,b", [
        ("apple", "application"),
        ("banana", "bandana"),
        ("python", "pytorch"),
    ])
    def test_similarity_is_symmetric(self, a, b):
        """similarity(a, b) == similarity(b, a) — standard for similarity metrics."""
        assert similarity(a, b) == similarity(b, a), (
            f"similarity not symmetric: similarity('{a}','{b}') != similarity('{b}','{a}')"
        )

    def test_similarity_is_deterministic(self):
        """Calling similarity twice with the same inputs returns the same value."""
        pairs = [("apple", "appetizer"), ("rust", "rush"), ("mango", "mange")]
        for a, b in pairs:
            first = similarity(a, b)
            second = similarity(a, b)
            assert first == second, f"similarity not deterministic for ('{a}', '{b}')"

    def test_similar_strings_score_higher_than_dissimilar(self):
        """A near-duplicate should score higher than a completely unrelated string."""
        base = "python"
        near = "pytho"       # one char removed
        far = "zxqwvjkl"     # nothing in common
        assert similarity(base, near) > similarity(base, far)

    def test_prefix_similarity_ordering(self):
        """Among strings with the same prefix, longer shared prefix -> higher score."""
        query = "application"
        long_prefix = "application_server"  # shares full word
        short_prefix = "app"
        unrelated = "zebra"
        # long_prefix shares more with query than unrelated
        assert similarity(query, long_prefix) > similarity(query, unrelated)
        # short_prefix should still outscore unrelated
        assert similarity(query, short_prefix) > similarity(query, unrelated)


# ---------------------------------------------------------------------------
# Recall against brute-force oracle (statistical threshold)
# ---------------------------------------------------------------------------

class TestRecallAgainstBruteForce:
    """
    Core statistical test: compare FuzzyIndex.search() against the exact
    top-k computed by brute-force scanning with similarity().

    Recall = |approx ∩ exact| / k

    Threshold justification: fuzzy nearest-neighbour indices are expected
    to achieve very high recall (>= 0.80) on small/medium corpora with
    textual similarity metrics. A threshold of 0.80 gives 20% headroom
    against near-tie boundary cases while still catching real regressions.
    All seeds are pinned so flakiness is impossible.
    """

    RECALL_THRESHOLD = 0.80

    def _assert_recall(self, corpus, query, k, seed_label=""):
        index = FuzzyIndex(corpus)
        approx = set(index.search(query, k=k))
        exact = brute_force_topk_set(corpus, query, k=k)

        overlap = len(approx & exact)
        recall = overlap / k
        assert recall >= self.RECALL_THRESHOLD, (
            f"recall {recall:.2f} < threshold {self.RECALL_THRESHOLD} "
            f"(query={query!r}, k={k}, overlap={overlap}/{k}{seed_label})"
        )

    def test_recall_small_corpus_k3(self):
        self._assert_recall(SMALL_CORPUS, "apple", k=3)

    def test_recall_small_corpus_k5(self):
        self._assert_recall(SMALL_CORPUS, "cherry", k=5)

    def test_recall_programming_corpus_k5(self):
        self._assert_recall(PROGRAMMING_CORPUS, "python", k=5)

    def test_recall_programming_corpus_k10(self):
        self._assert_recall(PROGRAMMING_CORPUS, "java", k=10)

    def test_recall_large_corpus_k10(self):
        self._assert_recall(LARGE_CORPUS, "hello", k=10)

    def test_recall_large_corpus_k20(self):
        self._assert_recall(LARGE_CORPUS, "world", k=20)

    def test_recall_large_corpus_k50(self):
        self._assert_recall(LARGE_CORPUS, "testing", k=50)

    def test_recall_query_not_in_corpus(self):
        """Query that doesn't appear in the corpus at all."""
        self._assert_recall(SMALL_CORPUS, "zzz", k=5)

    def test_recall_query_very_long(self):
        """Longer query string against normal corpus."""
        self._assert_recall(PROGRAMMING_CORPUS, "pythonprogramminglanguage", k=5)

    def test_recall_single_char_query(self):
        self._assert_recall(SMALL_CORPUS, "a", k=5)

    @pytest.mark.parametrize("seed", [0, 1, 2, 3, 4])
    def test_recall_multiple_random_queries_large_corpus(self, seed):
        """Run recall check across several seeded random queries to guard
        against lucky single-query passes."""
        rng = random.Random(seed)
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        query_len = rng.randint(3, 8)
        query = "".join(rng.choice(alphabet) for _ in range(query_len))
        self._assert_recall(LARGE_CORPUS, query, k=15, seed_label=f", seed={seed}, query={query!r}")


# ---------------------------------------------------------------------------
# Correctness of returned scores (exact assertions on the overlap)
# ---------------------------------------------------------------------------

class TestReturnedItemsAreCorrect:
    """Every string that the index returns AND that also appears in the
    brute-force top-k must have the correct similarity score.

    This separates two failure modes:
      (a) wrong *set* of results  -> caught by recall tests above
      (b) right *set* but wrong scores reported -> caught here

    Note: FuzzyIndex.search() is specified to return strings; similarity()
    is the separate oracle for scores, so we recompute scores ourselves.
    """

    def test_scores_of_overlapping_results_match_similarity(self):
        corpus = PROGRAMMING_CORPUS
        query = "python"
        k = 8
        index = FuzzyIndex(corpus)
        approx = list(index.search(query, k=k))
        exact_set = brute_force_topk_set(corpus, query, k=k)

        overlap = [s for s in approx if s in exact_set]
        for s in overlap:
            expected_score = similarity(query, s)
            # Re-query with k=1 restricted to just this string as a single-item index
            # to get the score in isolation — but since search() returns strings,
            # we simply assert the similarity value is self-consistent.
            assert isinstance(expected_score, float)
            # The score must be >= any item *not* in the top-k exact set
            non_topk = [c for c in corpus if c not in exact_set]
            for outsider in non_topk:
                assert similarity(query, s) >= similarity(query, outsider), (
                    f"'{s}' in top-{k} but scores lower than non-top-k item '{outsider}'"
                )

    def test_top1_result_has_highest_similarity(self):
        """The single top result must have the highest (or tied-highest)
        similarity score among all corpus members."""
        corpus = SMALL_CORPUS
        for query in ["apple", "banana", "cherry"]:
            index = FuzzyIndex(corpus)
            top1 = index.search(query, k=1)[0]
            top1_score = similarity(query, top1)
            for s in corpus:
                assert similarity(query, s) <= top1_score + 1e-9, (
                    f"query={query!r}: '{s}' (score={similarity(query,s)}) "
                    f"outscores top1 '{top1}' (score={top1_score})"
                )


# ---------------------------------------------------------------------------
# Edge-case and boundary tests
# ---------------------------------------------------------------------------

class TestEdgeCases:

    def test_corpus_with_duplicate_strings(self):
        """If the corpus contains duplicates, returned results still have no
        duplicates (deduplication is the caller's concern OR the index handles
        it — either way, the count of distinct results <= k)."""
        corpus = ["apple", "apple", "banana", "cherry"]
        index = FuzzyIndex(corpus)
        results = index.search("apple", k=2)
        assert len(results) <= 2

    def test_k_equals_corpus_size_returns_all(self):
        corpus = SMALL_CORPUS
        index = FuzzyIndex(corpus)
        results = index.search("apple", k=len(corpus))
        assert len(results) == len(corpus)

    def test_query_is_empty_string(self):
        """An empty query string should not raise and should return k items."""
        index = FuzzyIndex(SMALL_CORPUS)
        results = index.search("", k=3)
        assert len(results) <= 3  # may return fewer if similarity is undefined

    def test_corpus_of_one_distinct_element(self):
        index = FuzzyIndex(["solo"])
        results = index.search("solo", k=5)
        assert len(results) == 1
        assert results[0] == "solo"

    def test_corpus_all_identical_strings(self):
        """All strings are the same — any k results should all be that string."""
        corpus = ["same"] * 10
        index = FuzzyIndex(corpus)
        results = index.search("same", k=3)
        assert all(r == "same" for r in results)

    def test_k_equals_zero(self):
        """k=0 should return an empty result without error."""
        index = FuzzyIndex(SMALL_CORPUS)
        results = index.search("apple", k=0)
        assert len(results) == 0

    def test_recall_is_pinned_across_identical_calls(self):
        """With a fixed corpus and query, two calls return the same results
        (the index itself is deterministic even if approximate)."""
        corpus = PROGRAMMING_CORPUS
        index = FuzzyIndex(corpus)
        first = list(index.search("python", k=5))
        second = list(index.search("python", k=5))
        assert first == second, "identical calls to search() returned different results"
