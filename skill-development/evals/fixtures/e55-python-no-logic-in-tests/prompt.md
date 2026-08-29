# E55 — Upgrade: green tests, but users report malformed URLs

You are upgrading the test suite for a small URL-building module. Users have
reported profile links containing double slashes
(e.g. `https://example.com//users/bob`), but the test suite below is green.

`urls.py`:

```python
BASE_URL = "https://example.com/"


def profile_url(base, username):
    return base + "/users/" + username


def avatar_url(base, username, size):
    return base + "/users/" + username + "/avatar?size=" + str(size)
```

`tests/test_urls.py`:

```python
from urls import BASE_URL, profile_url, avatar_url


def test_profile_url():
    assert profile_url(BASE_URL, "bob") == BASE_URL + "/users/" + "bob"


def test_avatar_url():
    assert avatar_url(BASE_URL, "bob", 64) == (
        BASE_URL + "/users/" + "bob" + "/avatar?size=" + str(64)
    )
```

Task: write the upgraded `tests/test_urls.py` (a `.py` file) so the suite
catches this bug and this class of bug. The deliverable is the test file; you
may add brief comments or a short note about anything the production code
needs, and you should report what the upgraded tests do against the current
implementation.
