"""Tests for top_phrases through its public interface.

Survivor 3 is a real gap: nothing tested a phrase scoring exactly MIN_SCORE.
Survivors 1 and 2 are equivalent through the public interface: top_phrases
de-duplicates phrases, so the tie-break never compares two equal phrases, and the
cache only changes speed, not results. Killing them would mean testing private
helpers or poisoning the cache, so they are classified, not chased.
"""
from keyphrase import top_phrases


def test_phrase_scoring_exactly_min_score_is_kept():
    assert top_phrases("data, ab") == ["data"]


def test_strongest_first():
    assert top_phrases("zeta beta, alpha gamma, quartzite") == ["quartzite", "alpha gamma", "zeta beta"]


def test_equal_scores_are_alphabetical():
    assert top_phrases("gamma, delta") == ["delta", "gamma"]


def test_duplicates_ignoring_case_count_once():
    assert top_phrases("Data Model, data model") == ["Data Model"]


def test_limit():
    assert top_phrases("alpha, delta, gamma", limit=2) == ["alpha", "delta"]
