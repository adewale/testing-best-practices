import pytest

from search import SQL


@pytest.mark.parametrize(
    "fragment",
    ["SELECT title", "WHERE title LIKE ?", "ORDER BY score DESC", "LIMIT ?"],
)
def test_sql_contains(fragment):
    assert fragment in SQL
