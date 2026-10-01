from keyphrase import top_phrases


def test_strongest_first():
    assert top_phrases("zetas beta, alpha gamma, quartzite") == ["quartzite", "alpha gamma", "zetas beta"]


def test_low_scores_dropped():
    assert top_phrases("ab, quartzite") == ["quartzite"]
