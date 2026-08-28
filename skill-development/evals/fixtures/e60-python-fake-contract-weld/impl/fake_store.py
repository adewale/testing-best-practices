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
