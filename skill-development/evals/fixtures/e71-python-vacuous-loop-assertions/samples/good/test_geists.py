from geists import suggest

NOTES = [
    {"title": "A", "links": ["b", "c"]},
    {"title": "B", "links": []},
    {"title": "C", "links": ["a", "b", "d"]},
]


def test_suggests_every_note_that_meets_the_link_threshold():
    assert suggest(NOTES) == [
        "Revisit A: it connects 2 ideas",
        "Revisit C: it connects 3 ideas",
    ]


def test_note_below_threshold_is_not_suggested():
    assert suggest([{"title": "B", "links": ["x"]}]) == []


def test_every_suggestion_is_a_revisit_line():
    result = suggest(NOTES)
    assert result, "fixture notes must produce suggestions"
    assert all(s.startswith("Revisit ") for s in result)
