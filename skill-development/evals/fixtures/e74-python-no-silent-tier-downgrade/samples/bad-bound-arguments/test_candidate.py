from unittest.mock import MagicMock

from search import search


def test_partial_search_parameters():
    connection = MagicMock()
    search(connection, "testing", limit=2)
    assert connection.execute.call_args.args[1] == ("%testing%", 2)
