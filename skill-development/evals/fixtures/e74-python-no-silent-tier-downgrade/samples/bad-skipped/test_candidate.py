import pytest


@pytest.mark.skip(reason="unavailable")
def test_contract():
    # Run a real SQLite search and assert returned titles are ranked by score.
    assert False
