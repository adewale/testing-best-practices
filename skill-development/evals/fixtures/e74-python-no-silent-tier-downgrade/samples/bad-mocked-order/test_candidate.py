import sqlite3
from unittest.mock import Mock

from search import search


def test_mock_receives_ranked_partial_query():
    with sqlite3.connect(":memory:") as scratch:
        assert scratch.execute("SELECT 1").fetchone() == (1,)
    connection = Mock()
    connection.execute.return_value = [("Best",), ("Next",)]
    assert search(connection, "testing", 2) == ["Best", "Next"]
    query, parameters = connection.execute.call_args.args
    assert "ORDER BY score DESC" in query
    assert parameters == ("%testing%", 2)


def test_real_search_checks_membership_only():
    with sqlite3.connect(":memory:") as db:
        db.execute("CREATE TABLE articles (title TEXT, score REAL)")
        db.executemany("INSERT INTO articles VALUES (?, ?)", [("A key", 9), ("B key", 2)])
        assert set(search(db, "key")) == {"A key", "B key"}
