import sqlite3
from contextlib import closing

import pytest
from search import search as find_titles


@pytest.fixture
def best_match(tmp_path):
    class Reader:
        def __init__(self, database):
            self.database = database

        def execute(self, statement, parameters):
            return self.database.execute(statement, parameters).fetchall()

    with closing(sqlite3.connect(tmp_path / "articles.db")) as database:
        database.execute("CREATE TABLE articles (title TEXT, score REAL)")
        database.executemany(
            "INSERT INTO articles (score, title) VALUES (?, ?)",
            [(12, "Rain in July"), (30, "Dry season"), (20, "Rain in May")],
        )
        return find_titles(Reader(database), "Rain", limit=1)


def test_best_partial_match_is_first(best_match):
    assert best_match == ["Rain in May"]
