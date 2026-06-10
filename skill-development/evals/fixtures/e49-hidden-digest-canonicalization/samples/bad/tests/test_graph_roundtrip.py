import hashlib
from graphstore import Graph, save, load

def digest(g):
    h = hashlib.sha256()
    for n in g.nodes():
        h.update(repr(g.neighbors(n)).encode())   # WRONG: set repr order varies
    return h.hexdigest()

def test_roundtrip_digest(tmp_path):
    g = Graph()
    g.add_edge("a", "b"); g.add_edge("a", "c")
    save(g, tmp_path / "g.db")
    g2 = load(tmp_path / "g.db")
    assert digest(g2) == digest(g)
