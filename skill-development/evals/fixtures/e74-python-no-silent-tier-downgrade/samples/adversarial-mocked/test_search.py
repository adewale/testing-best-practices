from unittest.mock import MagicMock

from search import SQL, search


def test_search_executes_ranked_query():
    conn = MagicMock()
    conn.execute.return_value = [("Property testing",), ("Testing in Go",)]
    assert search(conn, "testing") == ["Property testing", "Testing in Go"]
    conn.execute.assert_called_once()
    assert conn.execute.call_args.args[0] == SQL
