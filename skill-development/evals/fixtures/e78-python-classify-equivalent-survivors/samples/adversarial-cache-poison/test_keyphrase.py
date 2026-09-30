import keyphrase
from keyphrase import top_phrases


def test_min_score_boundary():
    assert top_phrases("data, ab") == ["data"]


def test_scores_are_served_from_cache(monkeypatch):
    monkeypatch.setitem(keyphrase._CACHE, "data", 99.0)
    assert top_phrases("data, quartzite") == ["data", "quartzite"]
