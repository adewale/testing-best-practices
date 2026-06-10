import random
import pytest
from graphstore import Graph, save, load


def build_seeded_graph(rng: random.Random, num_edges: int = 20) -> Graph:
    """Build a graph with a variety of edges using a seeded RNG."""
    g = Graph()
    node_pool = [f"node_{i}" for i in range(10)]
    # Add some edges with typical names
    for _ in range(num_edges):
        a = rng.choice(node_pool)
        b = rng.choice(node_pool)
        if a != b:
            g.add_edge(a, b)
    # Add edges with awkward names: unicode, spaces, empty-ish strings
    g.add_edge("café", "naïve")
    g.add_edge("node with spaces", "another node")
    g.add_edge("unicode_中文", "ascii")
    # Add an isolated single-connection node
    g.add_edge("leaf", "node_0")
    return g


def canonical_dump(g: Graph) -> dict:
    """
    Produce a canonical, fully deterministic representation of the graph.

    Nodes and neighbor sets are both sorted so that unordered iteration
    does not cause spurious failures.
    """
    nodes = sorted(g.nodes())
    adjacency = {node: sorted(g.neighbors(node)) for node in nodes}
    return {"nodes": nodes, "adjacency": adjacency}


@pytest.mark.parametrize("seed", [1234, 5678, 9999])
def test_save_load_roundtrip_identity(tmp_path, seed):
    """
    Full whole-state identity check: save then load must reproduce the
    exact same graph for multiple seeded inputs.
    """
    g = build_seeded_graph(random.Random(seed), num_edges=25)
    before = canonical_dump(g)

    path = tmp_path / f"graph_{seed}"
    save(g, path)
    reloaded = load(path)
    after = canonical_dump(reloaded)

    assert after == before, (
        f"Roundtrip identity failed for seed={seed}.\n"
        f"Before: {before}\n"
        f"After:  {after}"
    )


def test_roundtrip_preserves_all_nodes(tmp_path):
    """
    Nodes that were added only via edges must survive the roundtrip.
    """
    g = build_seeded_graph(random.Random(42))
    original_nodes = sorted(g.nodes())

    save(g, tmp_path / "graph")
    reloaded = load(tmp_path / "graph")

    assert sorted(reloaded.nodes()) == original_nodes


def test_roundtrip_preserves_neighbor_sets(tmp_path):
    """
    For every node, the neighbor set after load must equal the neighbor
    set before save. Neighbors are compared as sets to avoid any ordering
    sensitivity, but canonical_dump also covers this; this test surfaces
    the failing node explicitly.
    """
    g = build_seeded_graph(random.Random(7))
    save(g, tmp_path / "graph")
    reloaded = load(tmp_path / "graph")

    for node in g.nodes():
        assert reloaded.neighbors(node) == g.neighbors(node), (
            f"Neighbor set mismatch for node {node!r}: "
            f"expected {sorted(g.neighbors(node))}, "
            f"got {sorted(reloaded.neighbors(node))}"
        )


def test_roundtrip_undirected_symmetry_preserved(tmp_path):
    """
    add_edge is undirected: b must appear in neighbors(a) and vice versa.
    This symmetry must survive a save/load cycle.
    """
    g = Graph()
    g.add_edge("X", "Y")
    g.add_edge("Y", "Z")

    save(g, tmp_path / "graph")
    reloaded = load(tmp_path / "graph")

    assert "Y" in reloaded.neighbors("X")
    assert "X" in reloaded.neighbors("Y")
    assert "Z" in reloaded.neighbors("Y")
    assert "Y" in reloaded.neighbors("Z")


def test_roundtrip_empty_graph(tmp_path):
    """
    An empty graph (no edges, no nodes) must roundtrip cleanly.
    """
    g = Graph()
    before = canonical_dump(g)

    save(g, tmp_path / "empty_graph")
    reloaded = load(tmp_path / "empty_graph")

    assert canonical_dump(reloaded) == before


def test_roundtrip_single_edge(tmp_path):
    """
    The minimal non-trivial graph — one edge between two nodes.
    """
    g = Graph()
    g.add_edge("alpha", "beta")
    before = canonical_dump(g)

    save(g, tmp_path / "single_edge")
    reloaded = load(tmp_path / "single_edge")

    assert canonical_dump(reloaded) == before


def test_roundtrip_awkward_node_names(tmp_path):
    """
    Node names with unicode, spaces, and punctuation must survive verbatim.
    """
    g = Graph()
    g.add_edge("café", "naïve")
    g.add_edge("node with spaces", "another node")
    g.add_edge("unicode_中文", "ascii")
    before = canonical_dump(g)

    save(g, tmp_path / "awkward")
    reloaded = load(tmp_path / "awkward")

    assert canonical_dump(reloaded) == before


def test_roundtrip_duplicate_add_edge_is_idempotent(tmp_path):
    """
    Adding the same edge multiple times should not inflate neighbor sets.
    The graph state after roundtrip must reflect idempotent edge insertion.
    """
    g = Graph()
    g.add_edge("A", "B")
    g.add_edge("A", "B")
    g.add_edge("B", "A")
    before = canonical_dump(g)

    save(g, tmp_path / "dedup")
    reloaded = load(tmp_path / "dedup")

    assert canonical_dump(reloaded) == before


def test_independent_saves_do_not_interfere(tmp_path):
    """
    Two graphs saved to different paths must load independently without
    cross-contamination.
    """
    g1 = Graph()
    g1.add_edge("1a", "1b")

    g2 = Graph()
    g2.add_edge("2a", "2b")
    g2.add_edge("2b", "2c")

    save(g1, tmp_path / "g1")
    save(g2, tmp_path / "g2")

    r1 = load(tmp_path / "g1")
    r2 = load(tmp_path / "g2")

    assert canonical_dump(r1) == canonical_dump(g1)
    assert canonical_dump(r2) == canonical_dump(g2)


def test_overwrite_save_reflects_latest_state(tmp_path):
    """
    Saving a graph twice to the same path: the second save must overwrite
    the first so that load returns the latest state.
    """
    g = Graph()
    g.add_edge("old_a", "old_b")
    path = tmp_path / "overwrite"
    save(g, path)

    g.add_edge("new_x", "new_y")
    save(g, path)
    reloaded = load(path)

    assert canonical_dump(reloaded) == canonical_dump(g)
    assert "new_x" in reloaded.nodes()
    assert "new_y" in reloaded.nodes()
