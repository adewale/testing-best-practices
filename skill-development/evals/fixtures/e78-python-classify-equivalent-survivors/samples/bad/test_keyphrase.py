import keyphrase
from keyphrase import _before, top_phrases


def test_tie_break_is_strict():
    assert _before(("same", 4.0), ("same", 4.0)) is False


def test_cache_is_used():
    keyphrase._CACHE["data"] = 99.0
    try:
        assert top_phrases("data, quartzite")[0] == "data"
    finally:
        keyphrase._CACHE.clear()


def test_min_score_boundary():
    assert top_phrases("data, ab") == ["data"]
