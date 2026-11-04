"""
The JSON-LD serializer writes every subject of a graph.

It started from IRI subjects and from blank nodes nothing refers to, and
reached the other blank nodes through references. Blank nodes that only refer
to each other, in a cycle, have no such entry point, so all of their triples
were silently left out: ``_:a ex:knows _:b . _:b ex:knows _:a`` serialized to
``[]``. The Serialize RDF as JSON-LD Algorithm (JSON-LD 1.1 Processing
Algorithms and API, section 8.4) appends every node with a property to the
result, referenced or not.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

import pytest

from rdflib import RDF, BNode, Dataset, Graph, Literal, Namespace
from rdflib.collection import Collection
from rdflib.compare import isomorphic

NS = Namespace("http://example.org/ns/")
VOCAB_CONTEXT = {"@vocab": str(NS)}
# A coercing term writes a reference and queues the node it refers to.
ID_CONTEXT = {"knows": {"@id": str(NS.knows), "@type": "@id"}}


def _two_node_cycle(g: Graph) -> None:
    a, b = BNode(), BNode()
    g.add((a, NS.knows, b))
    g.add((b, NS.knows, a))
    g.add((a, NS.name, Literal("a")))


def _self_reference(g: Graph) -> None:
    a = BNode()
    g.add((a, NS.knows, a))
    g.add((a, NS.name, Literal("a")))


def _self_referencing_list_cell(g: Graph) -> None:
    cell = BNode()
    g.add((cell, RDF.first, Literal("x")))
    g.add((cell, RDF.rest, cell))


def _cyclic_list_chain(g: Graph) -> None:
    c1, c2 = BNode(), BNode()
    g.add((c1, RDF.first, Literal("x")))
    g.add((c1, RDF.rest, c2))
    g.add((c2, RDF.first, Literal("y")))
    g.add((c2, RDF.rest, c1))


def _list_containing_itself(g: Graph) -> None:
    head = BNode()
    g.add((head, RDF.first, head))
    g.add((head, RDF.rest, RDF.nil))


def _lists_containing_each_other(g: Graph) -> None:
    h1, h2 = BNode(), BNode()
    g.add((h1, RDF.first, h2))
    g.add((h1, RDF.rest, RDF.nil))
    g.add((h2, RDF.first, h1))
    g.add((h2, RDF.rest, RDF.nil))


CYCLES: list[Callable[[Graph], None]] = [
    _two_node_cycle,
    _self_reference,
    _self_referencing_list_cell,
    _cyclic_list_chain,
    _list_containing_itself,
    _lists_containing_each_other,
]
CYCLE_IDS = [
    "two-node-cycle",
    "self-reference",
    "self-referencing-cell",
    "cyclic-chain",
    "list-containing-itself",
    "lists-containing-each-other",
]


@pytest.mark.parametrize(
    "context", [None, VOCAB_CONTEXT, ID_CONTEXT], ids=["plain", "vocab", "id-term"]
)
@pytest.mark.parametrize("build", CYCLES, ids=CYCLE_IDS)
def test_a_blank_node_cycle_without_an_entry_point_round_trips(
    build: Callable[[Graph], None], context: dict[str, Any] | None
) -> None:
    g = Graph()
    build(g)

    data = g.serialize(format="json-ld", context=context)
    g2 = Graph()
    g2.parse(data=data, format="json-ld")

    assert isomorphic(g, g2)


@pytest.mark.parametrize("build", CYCLES, ids=CYCLE_IDS)
def test_a_blank_node_cycle_in_a_named_graph_round_trips(
    build: Callable[[Graph], None],
) -> None:
    ds = Dataset()
    build(ds.graph(NS.g1))

    data = ds.serialize(format="json-ld")
    ds2 = Dataset()
    ds2.parse(data=data, format="json-ld")

    assert isomorphic(ds.graph(NS.g1), ds2.graph(NS.g1))


@pytest.mark.parametrize("build", CYCLES, ids=CYCLE_IDS)
def test_a_blank_node_cycle_in_the_default_graph_round_trips(
    build: Callable[[Graph], None],
) -> None:
    ds = Dataset()
    build(ds.default_graph)
    ds.graph(NS.g1).add((NS.s, NS.p, Literal("named")))

    data = ds.serialize(format="json-ld")
    ds2 = Dataset()
    ds2.parse(data=data, format="json-ld")

    assert isomorphic(ds.default_graph, ds2.default_graph)
    assert isomorphic(ds.graph(NS.g1), ds2.graph(NS.g1))


def test_a_cycle_beside_reachable_nodes_round_trips() -> None:
    g = Graph()
    _two_node_cycle(g)
    reached = BNode()
    g.add((NS.s, NS.p, reached))
    g.add((reached, NS.name, Literal("reached")))

    data = g.serialize(format="json-ld")
    g2 = Graph()
    g2.parse(data=data, format="json-ld")

    assert isomorphic(g, g2)


@pytest.mark.parametrize("list_first", [True, False], ids=["list-first", "cycle-first"])
def test_a_list_owned_by_a_cycle_node_is_written_once(list_first: bool) -> None:
    """Whichever side the store yields first, the list is inlined once.

    ``SimpleMemory`` yields triples in insertion order, so the order is fixed.
    """
    g = Graph(store="SimpleMemory")
    a, b, head = BNode(), BNode(), BNode()
    if list_first:
        Collection(g, head, [Literal("x")])
    g.add((a, NS.knows, b))
    g.add((b, NS.knows, a))
    g.add((a, NS.items, head))
    if not list_first:
        Collection(g, head, [Literal("x")])

    data = g.serialize(format="json-ld")
    g2 = Graph()
    g2.parse(data=data, format="json-ld")

    assert str(RDF.first) not in data
    assert data.count("@list") == 1
    assert isomorphic(g, g2)


def test_a_cycle_reached_from_an_entry_point_is_still_written_once() -> None:
    g = Graph()
    a, b = BNode(), BNode()
    g.add((NS.s, NS.p, a))
    g.add((a, NS.knows, b))
    g.add((b, NS.knows, a))

    data = g.serialize(format="json-ld")
    g2 = Graph()
    g2.parse(data=data, format="json-ld")

    assert len(json.loads(data)) == 3
    assert isomorphic(g, g2)
