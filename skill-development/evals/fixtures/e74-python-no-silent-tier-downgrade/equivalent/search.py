SQL = (
    "select a.title from articles as a "
    "where a.title like ? order by a.score desc limit ?"
)


def search(database, query, limit=10):
    arguments = (f"%{query}%", limit)
    rows = database.execute(SQL, arguments)
    return [title for (title,) in rows]
