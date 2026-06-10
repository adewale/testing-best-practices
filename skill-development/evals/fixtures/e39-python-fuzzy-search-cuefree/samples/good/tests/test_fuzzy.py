from fuzzy import FuzzyIndex, similarity

CORPUS = ["hello", "help", "hell", "halo", "world", "word", "wired",
          "spam", "spawn", "span", "spine", "shine"]

def exact_topk(q, k):
    return sorted(CORPUS, key=lambda s: similarity(q, s), reverse=True)[:k]

def test_search_overlaps_exact_ranking():
    idx = FuzzyIndex(CORPUS)
    k = 5
    for q in ["helo", "wrd", "spn"]:
        approx = set(idx.search(q, k))
        reference = set(exact_topk(q, k))
        overlap = len(approx & reference) / k
        assert overlap >= 0.6, f"overlap {overlap:.2f} too low for {q!r}"

def test_returned_items_are_genuinely_similar():
    idx = FuzzyIndex(CORPUS)
    results = idx.search("hello", 3)
    worst_returned = min(similarity("hello", s) for s in results)
    best_excluded = max(similarity("hello", s) for s in CORPUS if s not in results)
    # Allow approximation slack but the returned set must be near-optimal.
    assert worst_returned >= best_excluded - 0.2
