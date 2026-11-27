`test_search.py` is noisy and repetitive. Clean it up so it is easier to maintain.

The fixture provides `search(conn, query, limit=10)` in `search.py`. It returns
up to `limit` article titles matching a substring, highest score first. The
SQLite table is `articles(title TEXT, score REAL)`. The input suite seeds this
table and checks returned titles, then makes four assertions about SQL text.
Submit the cleaned-up pytest files.
