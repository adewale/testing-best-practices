import sqlite3

from search import SQL, search


def make_db():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE articles (title TEXT, score REAL)")
    conn.executemany(
        "INSERT INTO articles VALUES (?, ?)",
        [("Testing in Go", 0.4), ("Property testing", 0.9), ("Gardening", 0.7)],
    )
    return conn


def test_search_ranks_partial_matches_by_score():
    assert search(make_db(), "testing") == ["Property testing", "Testing in Go"]


def test_sql_orders_by_score():
    assert "ORDER BY score DESC" in SQL


def test_sql_has_limit():
    assert "LIMIT ?" in SQL


def test_sql_selects_title():
    assert SQL.startswith("SELECT title")


def test_sql_filters_on_title():
    assert "WHERE title LIKE ?" in SQL
