"""
Tests for the fuzzy module: FuzzyIndex and similarity.

Design rationale
----------------
- `similarity(a, b)` is a deterministic function with no external reference
  implementation, so we test it via pinned examples, algebraic properties, and
  invariants rather than a differential oracle (writing a reference similarity
  function would just duplicate the implementation and prove nothing).
- `FuzzyIndex.search(q, k)` is approximate: near-ties may differ between
  builds and platforms.  The oracle for correctness is `similarity` itself —
  we verify that every returned result is at least as similar to `q` as every
  non-returned result, using `similarity` as the ground-truth ranking.  This is
  a brute-force oracle: sort all candidates by similarity and compare the top-k
  set (not order) against what `search` returned.
"""

import pytest
from fuzzy import FuzzyIndex, similarity


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def brute_force_top_k(query: str, corpus: list[str], k: int) -> set[str]:
    """Return the set of k strings in corpus most similar to query."""
    ranked = sorted(corpus, key=lambda s: similarity(query, s), reverse=True)
    return set(ranked[:k])


def brute_force_scores(query: str, corpus: list[str]) -> dict[str, float]:
    return {s: similarity(query, s) for s in corpus}


# ---------------------------------------------------------------------------
# similarity — basic contract
# ---------------------------------------------------------------------------

class TestSimilarityContract:
    """Algebraic invariants that must hold for any similarity metric."""

    def test_identity_is_maximum_against_other_strings(self):
        """A string is at least as similar to itself as to any other string."""
        s = "hello"
        others = ["hell", "world", "helo", "", "h", "Hello", "HELLO"]
        self_sim = similarity(s, s)
        for other in others:
            assert similarity(s, other) <= self_sim, (
                f"similarity('{s}', '{other}') > similarity('{s}', '{s}')"
            )

    def test_symmetry(self):
        """similarity(a, b) == similarity(b, a)."""
        pairs = [
            ("cat", "bat"),
            ("kitten", "sitting"),
            ("", "hello"),
            ("abc", "abc"),
            ("fuzzy", "fuzz"),
        ]
        for a, b in pairs:
            assert similarity(a, b) == pytest.approx(similarity(b, a), abs=1e-9), (
                f"symmetry violated for ('{a}', '{b}')"
            )

    def test_returns_float(self):
        result = similarity("foo", "bar")
        assert isinstance(result, float)

    def test_identical_strings_return_same_score(self):
        """Any two calls with the same identical pair produce the same value."""
        val1 = similarity("repeat", "repeat")
        val2 = similarity("repeat", "repeat")
        assert val1 == val2

    def test_empty_string_against_itself(self):
        """Empty string vs itself should not raise and should be non-negative."""
        val = similarity("", "")
        assert isinstance(val, float)
        assert val >= 0.0

    def test_score_non_negative(self):
        """Scores must be >= 0 for all pairs."""
        pairs = [
            ("", "anything"),
            ("abc", "xyz"),
            ("a", "z"),
            ("hello world", "goodbye moon"),
        ]
        for a, b in pairs:
            assert similarity(a, b) >= 0.0


# ---------------------------------------------------------------------------
# similarity — ordering / ranking invariants
# ---------------------------------------------------------------------------

class TestSimilarityOrdering:
    """Higher similarity must agree with intuitive near/far distinctions
    for clear-cut cases (not near-ties)."""

    def test_closer_edit_ranks_higher(self):
        """'kiten' is one edit from 'kitten'; 'sitting' is many edits away."""
        ref = "kitten"
        close = "kiten"    # one deletion
        far = "sitting"    # multiple substitutions
        assert similarity(ref, close) > similarity(ref, far)

    def test_prefix_closer_than_unrelated(self):
        """A string that shares a long prefix should rank higher than
        a completely unrelated string of the same length."""
        ref = "programming"
        prefix_match = "program"
        unrelated = "zzzzzzz"
        assert similarity(ref, prefix_match) > similarity(ref, unrelated)

    def test_same_string_ranks_above_partial_match(self):
        ref = "fuzzy"
        assert similarity(ref, ref) > similarity(ref, "fuzz")

    def test_case_variants_rank_above_unrelated(self):
        """Case variants are closer than completely different strings."""
        ref = "Python"
        case_variant = "python"
        unrelated = "JavaScript"
        assert similarity(ref, case_variant) > similarity(ref, unrelated)


# ---------------------------------------------------------------------------
# FuzzyIndex — construction
# ---------------------------------------------------------------------------

class TestFuzzyIndexConstruction:
    def test_construct_with_list_of_strings(self):
        index = FuzzyIndex(["apple", "banana", "cherry"])
        assert index is not None

    def test_construct_empty(self):
        index = FuzzyIndex([])
        assert index is not None

    def test_construct_single_string(self):
        index = FuzzyIndex(["only"])
        assert index is not None

    def test_construct_with_duplicates(self):
        """Duplicates in the corpus must not raise."""
        index = FuzzyIndex(["dup", "dup", "dup"])
        assert index is not None


# ---------------------------------------------------------------------------
# FuzzyIndex.search — return type and shape
# ---------------------------------------------------------------------------

class TestFuzzyIndexSearchShape:
    def test_returns_list(self):
        index = FuzzyIndex(["apple", "banana"])
        result = index.search("apple", k=1)
        assert isinstance(result, list)

    def test_returns_strings(self):
        corpus = ["apple", "banana", "cherry"]
        index = FuzzyIndex(corpus)
        result = index.search("apple", k=2)
        for item in result:
            assert isinstance(item, str)

    def test_returns_k_results_when_corpus_large_enough(self):
        corpus = ["apple", "banana", "cherry", "date", "elderberry"]
        index = FuzzyIndex(corpus)
        for k in [1, 2, 3, 4, 5]:
            result = index.search("apricot", k=k)
            assert len(result) == k, f"Expected {k} results, got {len(result)}"

    def test_returns_at_most_corpus_size_when_k_exceeds_corpus(self):
        corpus = ["apple", "banana"]
        index = FuzzyIndex(corpus)
        result = index.search("apple", k=100)
        assert len(result) <= len(corpus)

    def test_returns_subset_of_corpus(self):
        corpus = ["apple", "banana", "cherry"]
        index = FuzzyIndex(corpus)
        result = index.search("apple", k=2)
        for item in result:
            assert item in corpus

    def test_empty_corpus_returns_empty(self):
        index = FuzzyIndex([])
        result = index.search("query", k=5)
        assert result == []

    def test_k_zero_returns_empty(self):
        index = FuzzyIndex(["apple", "banana"])
        result = index.search("apple", k=0)
        assert result == []


# ---------------------------------------------------------------------------
# FuzzyIndex.search — correctness via brute-force oracle
#
# The oracle: sort the full corpus by similarity(query, s) descending and take
# the top-k *set*.  We compare sets because near-ties are allowed to differ.
# To avoid false failures from near-ties we only run oracle checks on cases
# where the top-k and the rest have a clear gap.
# ---------------------------------------------------------------------------

FRUIT_CORPUS = [
    "apple", "application", "apply", "apt",
    "banana", "bandana", "band",
    "cherry", "chair", "charm",
    "grape", "graph", "grapefruit",
    "orange", "arrange", "range",
]

WORD_CORPUS = [
    "python", "pythons", "pythonic", "pith",
    "java", "javascript", "javadoc",
    "ruby", "rubric", "rub",
    "swift", "swiftly", "swifter",
    "go", "gone", "goal",
    "rust", "rustle", "rusk",
]


def has_clear_gap(query: str, corpus: list[str], k: int, gap: float = 0.05) -> bool:
    """Return True if there is a clear similarity gap between rank k and k+1."""
    scores = sorted(
        [similarity(query, s) for s in corpus],
        reverse=True,
    )
    if len(scores) <= k:
        return True  # no tie possible
    return (scores[k - 1] - scores[k]) >= gap


class TestFuzzyIndexSearchCorrectness:
    """Use similarity as a brute-force oracle to validate search results."""

    @pytest.mark.parametrize("query,k", [
        ("apple", 1),
        ("apple", 3),
        ("apply", 2),
        ("band", 2),
        ("cherry", 1),
        ("grapefruit", 3),
        ("range", 2),
    ])
    def test_top_k_set_matches_oracle_fruit(self, query, k):
        if not has_clear_gap(query, FRUIT_CORPUS, k):
            pytest.skip(f"Near-tie at rank {k} for query '{query}' — skip to avoid flakiness")
        index = FuzzyIndex(FRUIT_CORPUS)
        result_set = set(index.search(query, k=k))
        expected_set = brute_force_top_k(query, FRUIT_CORPUS, k)
        assert result_set == expected_set, (
            f"query='{query}', k={k}: got {result_set}, expected {expected_set}"
        )

    @pytest.mark.parametrize("query,k", [
        ("python", 1),
        ("pythonic", 2),
        ("java", 1),
        ("javascript", 2),
        ("ruby", 1),
        ("swift", 2),
        ("rust", 2),
    ])
    def test_top_k_set_matches_oracle_words(self, query, k):
        if not has_clear_gap(query, WORD_CORPUS, k):
            pytest.skip(f"Near-tie at rank {k} for query '{query}' — skip to avoid flakiness")
        index = FuzzyIndex(WORD_CORPUS)
        result_set = set(index.search(query, k=k))
        expected_set = brute_force_top_k(query, WORD_CORPUS, k)
        assert result_set == expected_set, (
            f"query='{query}', k={k}: got {result_set}, expected {expected_set}"
        )

    def test_exact_match_in_top_1(self):
        """When the query is in the corpus, it must be the top-1 result."""
        corpus = ["apple", "banana", "cherry", "date"]
        index = FuzzyIndex(corpus)
        for word in corpus:
            result = index.search(word, k=1)
            assert result[0] == word, (
                f"Expected exact match '{word}' as top-1, got '{result[0]}'"
            )

    def test_results_are_not_worse_than_excluded_items(self):
        """Every returned item must have similarity >= every non-returned item."""
        corpus = ["apple", "application", "apply", "banana", "cherry", "date"]
        index = FuzzyIndex(corpus)
        query = "appl"
        k = 2
        result = index.search(query, k=k)
        returned_set = set(result)
        excluded = [s for s in corpus if s not in returned_set]

        min_returned_score = min(similarity(query, s) for s in returned_set)
        for excl in excluded:
            excl_score = similarity(query, excl)
            # Allow near-ties (within a small epsilon)
            assert excl_score <= min_returned_score + 1e-9, (
                f"Excluded '{excl}' (score={excl_score:.4f}) is more similar than "
                f"returned item with min score {min_returned_score:.4f}"
            )

    def test_k1_returns_most_similar(self):
        """search(q, 1) must return the single most similar string."""
        corpus = FRUIT_CORPUS
        index = FuzzyIndex(corpus)
        queries = ["apple", "band", "grape", "orange"]
        for query in queries:
            scores = brute_force_scores(query, corpus)
            best = max(scores, key=scores.__getitem__)
            result = index.search(query, k=1)
            assert len(result) == 1
            # Allow tie: result[0] must be at least as good as best
            assert similarity(query, result[0]) >= similarity(query, best) - 1e-9, (
                f"query='{query}': got '{result[0]}' "
                f"(score={similarity(query, result[0]):.4f}), "
                f"expected '{best}' (score={similarity(query, best):.4f})"
            )


# ---------------------------------------------------------------------------
# FuzzyIndex.search — repeated / idempotent behaviour
# ---------------------------------------------------------------------------

class TestFuzzyIndexIdempotence:
    def test_repeated_search_same_result(self):
        """Calling search twice with the same args returns the same result."""
        index = FuzzyIndex(FRUIT_CORPUS)
        r1 = index.search("apple", k=3)
        r2 = index.search("apple", k=3)
        assert r1 == r2

    def test_multiple_queries_independent(self):
        """Different queries do not interfere with each other."""
        index = FuzzyIndex(WORD_CORPUS)
        r_python = index.search("python", k=2)
        r_java = index.search("java", k=2)
        # Results for one query must not contaminate the other
        r_python2 = index.search("python", k=2)
        assert r_python == r_python2

    def test_index_unchanged_after_search(self):
        """Searching does not modify subsequent searches for an unrelated query."""
        corpus = ["cat", "bat", "hat", "rat", "mat"]
        index = FuzzyIndex(corpus)
        index.search("cat", k=3)
        result_after = index.search("mat", k=2)
        # Should still return from the original corpus
        for item in result_after:
            assert item in corpus


# ---------------------------------------------------------------------------
# FuzzyIndex.search — edge cases
# ---------------------------------------------------------------------------

class TestFuzzyIndexEdgeCases:
    def test_query_not_in_corpus(self):
        """Query not present in the corpus must still return valid results."""
        corpus = ["apple", "banana", "cherry"]
        index = FuzzyIndex(corpus)
        result = index.search("zzzzzzz", k=2)
        assert len(result) == 2
        for item in result:
            assert item in corpus

    def test_empty_query_string(self):
        """Empty query must not raise and must return k results."""
        corpus = ["apple", "banana", "cherry"]
        index = FuzzyIndex(corpus)
        result = index.search("", k=2)
        assert isinstance(result, list)
        assert len(result) <= len(corpus)
        for item in result:
            assert item in corpus

    def test_corpus_with_empty_string(self):
        """Corpus containing empty string must not raise."""
        corpus = ["", "apple", "banana"]
        index = FuzzyIndex(corpus)
        result = index.search("apple", k=2)
        assert isinstance(result, list)

    def test_single_element_corpus_k1(self):
        corpus = ["only"]
        index = FuzzyIndex(corpus)
        result = index.search("query", k=1)
        assert result == ["only"]

    def test_single_element_corpus_k_larger(self):
        corpus = ["only"]
        index = FuzzyIndex(corpus)
        result = index.search("query", k=5)
        assert len(result) <= 1

    def test_long_strings(self):
        """Must handle long strings without raising."""
        long_a = "a" * 1000
        long_b = "b" * 1000
        corpus = [long_a, long_b, "short"]
        index = FuzzyIndex(corpus)
        result = index.search(long_a, k=2)
        assert isinstance(result, list)
        assert len(result) == 2

    def test_unicode_strings(self):
        """Must handle unicode without raising."""
        corpus = ["café", "naïve", "résumé", "hello", "world"]
        index = FuzzyIndex(corpus)
        result = index.search("cafe", k=2)
        assert isinstance(result, list)

    def test_whitespace_strings(self):
        corpus = ["hello world", "hello  world", "hello", "world"]
        index = FuzzyIndex(corpus)
        result = index.search("hello world", k=2)
        assert isinstance(result, list)
        for item in result:
            assert item in corpus

    def test_special_characters(self):
        corpus = ["foo.bar", "foo-bar", "foo_bar", "foobar"]
        index = FuzzyIndex(corpus)
        result = index.search("foo bar", k=2)
        assert isinstance(result, list)

    def test_k_equals_corpus_size(self):
        corpus = ["a", "b", "c", "d"]
        index = FuzzyIndex(corpus)
        result = index.search("a", k=4)
        assert len(result) == 4
        assert set(result) == set(corpus)
