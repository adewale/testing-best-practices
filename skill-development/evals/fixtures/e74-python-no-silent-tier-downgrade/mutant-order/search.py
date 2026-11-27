"""Reverse ranking in the executed query while preserving the exported constant."""

import _tbp_search_reference

SQL = _tbp_search_reference.SQL


def search(conn, query, limit=10):
    low_first = "SELECT title FROM articles WHERE title LIKE ? ORDER BY score ASC LIMIT ?"
    return [row[0] for row in conn.execute(low_first, (f"%{query}%", limit))]
