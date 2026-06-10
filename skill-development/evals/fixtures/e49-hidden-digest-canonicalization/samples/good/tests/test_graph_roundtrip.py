from graphstore import Graph, save, load

def build_graph():
    g = Graph()
    edges = [("a", "b"), ("a", "c"), ("b", "c"), ("c", "d"), ("d", "a"), ("e", "a")]
    for x, y in edges:
        g.add_edge(x, y)
    return g

def test_roundtrip_preserves_structure(tmp_path):
    g = build_graph()
    save(g, tmp_path / "g.db")
    g2 = load(tmp_path / "g.db")

    assert sorted(g2.nodes()) == sorted(g.nodes())
    for n in g.nodes():
        # Set equality is order-free; no textual dump, no unsorted hash.
        assert g2.neighbors(n) == g.neighbors(n), f"neighbors differ at {n}"

def test_roundtrip_of_empty_graph(tmp_path):
    g = Graph()
    save(g, tmp_path / "g.db")
    assert sorted(load(tmp_path / "g.db").nodes()) == []
