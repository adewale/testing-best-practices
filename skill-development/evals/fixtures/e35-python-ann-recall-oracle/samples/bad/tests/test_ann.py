from ann import AnnIndex

def test_query_returns_k():
    index = AnnIndex([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
    results = index.query([1.0, 0.0], k=2)
    assert len(results) == 2

def test_query_exact_match():
    index = AnnIndex([[1.0, 0.0], [0.0, 1.0]])
    # WRONG: pins an exact result set against an approximate algorithm
    assert index.query([1.0, 0.0], k=1) == [0]
