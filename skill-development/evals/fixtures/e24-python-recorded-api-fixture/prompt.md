# E24 Python Recorded API Fixture

Our Python API client tests monkeypatch `requests.get` to return a hand-written dict. The provider changed a field name and tests missed it. Upgrade the tests so provider shape drift is caught without live network calls in normal CI.
