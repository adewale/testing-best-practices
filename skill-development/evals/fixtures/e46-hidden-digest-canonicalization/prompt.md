# E46 (adversarial) Graph persistence with unordered neighbors

Module `graphstore`: `Graph` with `add_edge(a, b)`, `graph.nodes()` returning a list of node names, and `graph.neighbors(n)` returning a `set` whose iteration order is unspecified and varies between runs. `save(g, path)` / `load(path)`. Add pytest roundtrip tests for save/load.
