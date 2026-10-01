SQL = "SELECT title FROM articles WHERE title LIKE ? ORDER BY score DESC LIMIT ?"


def search(conn, query, limit=10):
    # Mutant: wildcards dropped, so partial-title matches silently vanish.
    return [row[0] for row in conn.execute(SQL, (query, limit))]
