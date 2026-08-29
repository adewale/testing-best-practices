# E60 — Write: keep the fake honest

Our unit tests use `FakeStore` as a stand-in for `RealStore`. Last quarter the
fake drifted from the real implementation — the fake returned `None` for a
missing key while `RealStore` raises `KeyError` — and a bug shipped because
every test exercised only the fake's behavior.

Both implementations are below. Keys and values are `str`. `RealStore` works
offline (SQLite, in-memory by default), so it is cheap to construct in a test.

`store.py`:

```python
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
```

`fake_store.py`:

```python
class FakeStore:
    """In-memory stand-in for RealStore used by unit tests."""

    def __init__(self):
        self._data = {}

    def set(self, key, value):
        self._data[key] = value

    def get(self, key):
        if key not in self._data:
            raise KeyError(key)
        return self._data[key]

    def delete(self, key):
        self._data.pop(key, None)
```

Task: add tests that keep `FakeStore` honest with respect to `RealStore`, so
a drift like the `None`-vs-`KeyError` incident cannot ship silently again.
Deliverable: `tests/test_store_contract.py` (pytest).
