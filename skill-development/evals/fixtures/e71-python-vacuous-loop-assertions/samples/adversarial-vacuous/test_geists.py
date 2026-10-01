from geists import suggest

NOTES = [{"title": "A", "links": ["b", "c"]}, {"title": "C", "links": ["a", "b", "d"]}]


def test_suggest_returns_a_list():
    result = suggest(NOTES)
    assert isinstance(result, list)
    assert len(result) >= 0
    for s in result:
        assert s.startswith("Revisit")
