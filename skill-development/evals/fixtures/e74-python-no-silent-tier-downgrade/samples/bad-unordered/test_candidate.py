import sqlite3

from search import search


def test_partial_matches_without_checking_rank():
    with sqlite3.connect(":memory:") as db:
        db.execute("CREATE TABLE articles (title TEXT, score REAL)")
        db.executemany("INSERT INTO articles VALUES (?, ?)", [("A news", 1), ("B news", 3)])
        assert set(search(db, "news")) == {"A news", "B news"}
