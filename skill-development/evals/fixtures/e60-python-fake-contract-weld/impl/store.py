import sqlite3


class RealStore:
    """Key-value store backed by SQLite. get() raises KeyError on missing keys."""

    def __init__(self, path=":memory:"):
        self._db = sqlite3.connect(path)
        self._db.execute("CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT)")

    def set(self, key, value):
        self._db.execute(
            "INSERT INTO kv(k, v) VALUES(?, ?) "
            "ON CONFLICT(k) DO UPDATE SET v=excluded.v",
            (key, value),
        )
        self._db.commit()

    def get(self, key):
        row = self._db.execute("SELECT v FROM kv WHERE k=?", (key,)).fetchone()
        if row is None:
            raise KeyError(key)
        return row[0]

    def delete(self, key):
        self._db.execute("DELETE FROM kv WHERE k=?", (key,))
        self._db.commit()
