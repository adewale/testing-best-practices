from fuzzy import FuzzyIndex

def test_search_hello():
    idx = FuzzyIndex(["hello", "help", "hell", "world"])
    # WRONG: pins an exact list for an approximate search
    assert idx.search("helo", 3) == ["hello", "help", "hell"]

def test_search_returns_k():
    idx = FuzzyIndex(["a", "b", "c", "d"])
    assert len(idx.search("a", 2)) == 2
