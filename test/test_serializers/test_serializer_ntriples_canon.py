import os
import subprocess
import sys

from rdflib import BNode, Graph, Literal, Namespace
from rdflib.compare import isomorphic

BUILD = """
from rdflib import RDF, BNode, Graph, Literal, Namespace
ns = Namespace("http://example.org/ns/")
g = Graph()
hub = BNode()
for i in range(4):
    g.add((ns[f"s{i}"], ns.ref, hub))
g.add((hub, ns.value, Literal("hub")))
cells = [BNode() for _ in range(4)]
for i, cell in enumerate(cells):
    g.add((cell, RDF.first, Literal(f"v{i}")))
    g.add((cell, RDF.rest, cells[i + 1] if i + 1 < len(cells) else RDF.nil))
g.add((ns.a, ns.items, cells[0]))
"""


def _graph() -> Graph:
    namespace: dict = {}
    exec(BUILD, namespace)
    return namespace["g"]


def test_canon_produces_identical_bytes_across_processes():
    """``canon=True`` must survive a change of process, which is the point of it.

    Hash seeds rather than repeated calls in one process: the store's iteration
    order is stable within a process, so repeating a call proves nothing.
    """
    script = (
        BUILD
        + """
import sys
sys.stdout.write(g.serialize(format="nt", canon=True))
"""
    )
    outputs = {
        subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
            check=True,
            env={**os.environ, "PYTHONHASHSEED": str(seed)},
        ).stdout
        for seed in (0, 1, 2, 3, 5, 8)
    }
    assert len(outputs) == 1, f"canon=True gave {len(outputs)} different documents"


def test_canon_output_is_sorted():
    lines = [
        line
        for line in _graph().serialize(format="nt", canon=True).splitlines()
        if line
    ]
    assert lines == sorted(lines)


def test_canon_preserves_the_graph():
    g = _graph()
    reparsed = Graph()
    reparsed.parse(data=g.serialize(format="nt", canon=True), format="nt")
    assert len(reparsed) == len(g)
    assert isomorphic(reparsed, g)


def test_canon_is_off_by_default():
    """Ordinary serialization must be untouched.

    Default output keeps the graph's own blank-node labels, so it differs from
    the canonicalized form -- which is what shows the parameter is doing
    something rather than being ignored.
    """
    g = _graph()
    default = g.serialize(format="nt")

    reparsed = Graph()
    reparsed.parse(data=default, format="nt")
    assert isomorphic(reparsed, g)
    assert len(default.splitlines()) == len(g)
    assert default != g.serialize(format="nt", canon=True)


def test_an_unrecognised_keyword_is_still_ignored():
    """The parameter is opt-in via kwargs; nothing else may start failing."""
    g = _graph()
    assert g.serialize(format="nt", something_else=True) == g.serialize(format="nt")


def test_canon_works_for_nt11():
    """NT11Serializer subclasses NTSerializer, so it inherits the parameter."""
    g = _graph()
    reparsed = Graph()
    reparsed.parse(data=g.serialize(format="nt11", canon=True), format="nt")
    assert isomorphic(reparsed, g)


def test_canon_on_an_empty_graph():
    assert Graph().serialize(format="nt", canon=True) == ""


def test_canon_relabels_blank_nodes_independently_of_their_input_names():
    """Canonicalization is what makes the sort meaningful across runs."""
    ns = Namespace("http://example.org/ns/")
    first, second = Graph(), Graph()
    for graph, name in ((first, "aaa"), (second, "zzz")):
        node = BNode(name)
        graph.add((ns.s, ns.p, node))
        graph.add((node, ns.q, Literal("v")))

    assert first.serialize(format="nt", canon=True) == second.serialize(
        format="nt", canon=True
    )
