from geists import suggest

NOTES = [
    {"title": "A", "links": ["b", "c"]},
    {"title": "B", "links": []},
    {"title": "C", "links": ["a", "b", "d"]},
]


def test_suggestions_are_strings():
    for s in suggest(NOTES):
        assert isinstance(s, str)


def test_suggestions_mention_revisit():
    for s in suggest(NOTES):
        assert s.startswith("Revisit")


def test_no_blank_suggestions():
    for s in suggest(NOTES):
        assert s.strip()
