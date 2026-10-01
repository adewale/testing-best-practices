import sqlite3

import pytest

from search import search


@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE articles (title TEXT, score REAL)")
    conn.executemany(
        "INSERT INTO articles VALUES (?, ?)",
        [("Testing in Go", 0.4), ("Property testing", 0.9), ("Gardening", 0.7)],
    )
    return conn


def test_partial_matches_ranked_by_score(db):
    assert search(db, "testing") == ["Property testing", "Testing in Go"]


def test_limit_caps_results(db):
    assert search(db, "testing", limit=1) == ["Property testing"]
