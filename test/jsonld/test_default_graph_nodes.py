"""
The JSON-LD serializer writes a dataset's default graph as top-level nodes.

A node object with ``@graph`` but without ``@id`` is a graph named by a new
blank node (Node Map Generation, JSON-LD 1.1 Processing Algorithms and API,
section 7.2.2), so the default graph's nodes must not be wrapped in one. The
serializer did that whenever the default graph had more than one node and the
dataset had named graphs, even empty ones: rdflib read it back as the default
graph, but other processors did not.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from rdflib import ConjunctiveGraph, Dataset, Graph, Literal, Namespace
from rdflib.compare import isomorphic

EX = Namespace("http://example.org/")
CONTEXTS = [
    pytest.param(None, id="no-context"),
    pytest.param({"@vocab": str(EX)}, id="vocab-context"),
]


def _top_level(data: str) -> list[dict[str, Any]]:
    """The top-level node and graph objects of a JSON-LD document."""
    doc = json.loads(data)
    if isinstance(doc, list):
        return doc
    if "@id" in doc or "@graph" not in doc:
        return [doc]
    return doc["@graph"]


def _dataset(default_nodes: int) -> Dataset:
    ds = Dataset()
    for index in range(default_nodes):
        ds.default_graph.add((EX[f"d{index}"], EX.p, Literal(f"default {index}")))
    ds.graph(EX.g).add((EX.n, EX.p, Literal("named")))
    return ds


def _round_trip(ds: Dataset, context: dict[str, Any] | None) -> tuple[str, Dataset]:
    data = ds.serialize(format="json-ld", context=context)
    ds2 = Dataset()
    ds2.parse(data=data, format="json-ld")
    return data, ds2


@pytest.mark.parametrize("context", CONTEXTS)
@pytest.mark.parametrize("default_nodes", [2, 3])
def test_default_graph_nodes_are_top_level_next_to_named_graphs(
    context: dict[str, Any] | None, default_nodes: int
) -> None:
    ds = _dataset(default_nodes)

    data, ds2 = _round_trip(ds, context)

    top_level = _top_level(data)
    assert all("@id" in obj for obj in top_level)
    graphs = [obj for obj in top_level if "@graph" in obj]
    assert len(graphs) == 1
    assert len(top_level) == default_nodes + 1
    assert isomorphic(ds.default_graph, ds2.default_graph)
    assert isomorphic(ds.graph(EX.g), ds2.graph(EX.g))


@pytest.mark.parametrize("context", CONTEXTS)
def test_a_named_graph_goes_into_the_default_node_of_its_name(
    context: dict[str, Any] | None,
) -> None:
    """The node and the graph share an "@id", so they are one object."""
    ds = _dataset(1)
    ds.default_graph.add((EX.g, EX.p, Literal("the graph's node")))

    data, ds2 = _round_trip(ds, context)

    (node,) = (obj for obj in _top_level(data) if "@graph" in obj)
    assert node["@id"] == str(EX.g)
    assert ("p" if context else str(EX.p)) in node
    assert isomorphic(ds.default_graph, ds2.default_graph)
    assert isomorphic(ds.graph(EX.g), ds2.graph(EX.g))


def test_default_graph_nodes_next_to_an_empty_named_graph_are_top_level() -> None:
    """An empty named graph is not written, but it made the wrapper appear."""
    ds = Dataset()
    ds.default_graph.add((EX.a, EX.p, Literal("a")))
    ds.default_graph.add((EX.b, EX.p, Literal("b")))
    ds.graph(EX.empty)

    data, ds2 = _round_trip(ds, None)

    assert all("@id" in obj for obj in _top_level(data))
    assert isomorphic(ds.default_graph, ds2.default_graph)


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_a_conjunctive_graph_default_context_is_top_level() -> None:
    cg = ConjunctiveGraph()
    cg.add((EX.a, EX.p, Literal("a")))
    cg.add((EX.b, EX.p, Literal("b")))
    cg.get_context(EX.g).add((EX.n, EX.p, Literal("named")))

    data = cg.serialize(format="json-ld")

    top_level = _top_level(data)
    assert all("@id" in obj for obj in top_level)
    assert {obj["@id"] for obj in top_level} == {str(EX.a), str(EX.b), str(EX.g)}


@pytest.mark.parametrize("context", CONTEXTS)
def test_a_single_default_node_is_still_top_level(
    context: dict[str, Any] | None,
) -> None:
    """Guard: this case was already written correctly."""
    ds = _dataset(1)

    data, ds2 = _round_trip(ds, context)

    assert all("@id" in obj for obj in _top_level(data))
    assert isomorphic(ds.default_graph, ds2.default_graph)


def test_a_plain_graph_is_still_a_list_of_nodes() -> None:
    """Guard: without a context, a graph is written as a bare node list."""
    g = Graph()
    g.add((EX.a, EX.p, Literal("a")))
    g.add((EX.b, EX.p, Literal("b")))

    doc = json.loads(g.serialize(format="json-ld"))

    assert isinstance(doc, list)
    assert sorted(node["@id"] for node in doc) == [str(EX.a), str(EX.b)]
