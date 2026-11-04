"""
The JSON-LD serializer keeps a Dataset's blank-node-named graphs as graphs.

An RDF dataset can name a graph by a blank node (RDF 1.1 Concepts, section
4), and JSON-LD writes it as ``{"@id": "_:b0", "@graph": [...]}``. The
serializer moved such a graph's triples into the default graph instead, and
did so by adding them to the Dataset's own default graph, so serializing
changed the data being serialized.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from rdflib import BNode, ConjunctiveGraph, Dataset, Literal, Namespace
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID

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


def _dataset(default_nodes: int, **kwargs: Any) -> Dataset:
    ds = Dataset(**kwargs)
    for index in range(default_nodes):
        ds.default_graph.add((EX[f"d{index}"], EX.p, Literal(f"default {index}")))
    ds.graph(BNode()).add((EX.b, EX.p, Literal("blank-node graph")))
    ds.graph(EX.g).add((EX.c, EX.p, Literal("IRI graph")))
    return ds


def _graph_sizes(ds: Dataset) -> dict[str, int]:
    """Graph sizes by kind of name, independent of blank node labels."""
    sizes: dict[str, int] = {}
    for g in ds.graphs():
        if g.identifier == DATASET_DEFAULT_GRAPH_ID:
            key = "default"
        elif isinstance(g.identifier, BNode):
            key = "blank node"
        else:
            key = str(g.identifier)
        if len(g):
            sizes[key] = sizes.get(key, 0) + len(g)
    return sizes


def test_serializing_does_not_change_the_dataset() -> None:
    ds = _dataset(1)
    before = {(g.identifier, len(g)) for g in ds.graphs()}

    ds.serialize(format="json-ld")

    assert {(g.identifier, len(g)) for g in ds.graphs()} == before
    assert len(ds.default_graph) == 1


@pytest.mark.parametrize("context", CONTEXTS)
@pytest.mark.parametrize("default_nodes", [0, 1, 2])
def test_a_blank_node_named_graph_stays_a_named_graph(
    context: dict[str, Any] | None, default_nodes: int
) -> None:
    ds = _dataset(default_nodes)

    data = ds.serialize(format="json-ld", context=context)
    ds2 = Dataset()
    ds2.parse(data=data, format="json-ld")

    assert _graph_sizes(ds2) == _graph_sizes(ds)
    top_level = _top_level(data)
    # Every graph object has a name, so none hides the default graph.
    assert all("@id" in obj for obj in top_level)
    assert any(obj["@id"].startswith("_:") and "@graph" in obj for obj in top_level)


def test_a_blank_node_naming_a_graph_and_a_node_is_one_object() -> None:
    """Like an IRI, the name of a graph and a default node is one object."""
    ds = Dataset()
    name = BNode()
    ds.default_graph.add((name, EX.p, Literal("the graph's node")))
    ds.graph(name).add((EX.b, EX.p, Literal("in the graph")))

    data = ds.serialize(format="json-ld")
    ds2 = Dataset()
    ds2.parse(data=data, format="json-ld")

    (obj,) = _top_level(data)
    assert obj["@id"] == name.n3()
    assert str(EX.p) in obj and "@graph" in obj
    assert _graph_sizes(ds2) == _graph_sizes(ds)


def test_a_default_union_dataset_keeps_its_blank_node_graph() -> None:
    ds = _dataset(1, default_union=True)

    data = ds.serialize(format="json-ld")
    ds2 = Dataset()
    ds2.parse(data=data, format="json-ld")

    assert _graph_sizes(ds2) == _graph_sizes(ds)


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_a_conjunctive_graph_still_merges_its_blank_node_graphs() -> None:
    """Guard: its default context has a blank-node name too, so its
    blank-node graphs are written as the default graph, as before, without
    changing the input."""
    cg = ConjunctiveGraph()
    cg.add((EX.a, EX.p, Literal("default")))
    cg.get_context(BNode()).add((EX.b, EX.p, Literal("blank-node graph")))
    cg.get_context(EX.g).add((EX.c, EX.p, Literal("IRI graph")))
    before = {(c.identifier, len(c)) for c in cg.contexts()}

    data = cg.serialize(format="json-ld")

    assert {(c.identifier, len(c)) for c in cg.contexts()} == before
    assert {obj["@id"] for obj in _top_level(data)} == {
        str(EX.a),
        str(EX.b),
        str(EX.g),
    }
