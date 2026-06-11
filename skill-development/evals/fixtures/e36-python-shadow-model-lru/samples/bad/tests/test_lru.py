from lru import LruCache

def test_put_then_get():
    c = LruCache(capacity=2)
    c.put("a", 1)
    assert c.get("a") == 1

def test_missing_key():
    c = LruCache(capacity=2)
    assert c.get("x") is None
