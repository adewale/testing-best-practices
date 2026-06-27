# E42 Python fuzzy search (cue-free)

A module `fuzzy` provides `FuzzyIndex(strings)` whose `search(q, k)` returns the k most similar strings to `q` — approximately: near-ties may differ between builds and platforms. The documented metric is the deterministic module function `similarity(a, b) -> float` (higher is more similar). Add pytest tests for `search`.
