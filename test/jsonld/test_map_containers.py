"""
JSON-LD 1.1 type, id and graph id maps whose entry values are arrays of node
objects, see https://github.com/RDFLib/rdflib/issues/3538.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from rdflib import RDF, BNode, Dataset, Literal, Namespace
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID as DEFAULT

EX = Namespace("http://example.org/")

CONTEXT = {
    "@version": 1.1,
    "ex": "http://example.org/",
    "Person": "ex:Person",
    "name": "ex:name",
    "byType": {"@id": "@graph", "@container": "@type"},
    "members": {"@id": "ex:members", "@container": "@type"},
    "byId": {"@id": "ex:byId", "@container": "@id"},
    "graphsById": {"@id": "ex:graphsById", "@container": ["@graph", "@id"]},
    "graphsByIndex": {"@id": "ex:graphsByIndex", "@container": ["@graph", "@index"]},
}

ALICE = {"@id": "ex:alice", "name": "Alice"}
BOB = {"@id": "ex:bob", "name": "Bob"}


def _parse_jsonld(data: dict[str, Any]) -> Dataset:
    ds = Dataset()
    ds.parse(data=json.dumps({"@context": CONTEXT, **data}), format="json-ld")
    return ds


@pytest.mark.parametrize(
    ["data", "expected"],
    [
        pytest.param(
            {"byType": {"Person": ALICE}},
            {
                (EX.alice, RDF.type, EX.Person, DEFAULT),
                (EX.alice, EX.name, Literal("Alice"), DEFAULT),
            },
            id="type-map-node",
        ),
        pytest.param(
            {"byType": {"Person": [ALICE, BOB]}},
            {
                (EX.alice, RDF.type, EX.Person, DEFAULT),
                (EX.alice, EX.name, Literal("Alice"), DEFAULT),
                (EX.bob, RDF.type, EX.Person, DEFAULT),
                (EX.bob, EX.name, Literal("Bob"), DEFAULT),
            },
            id="type-map-array",
        ),
        pytest.param(
            {"@id": "ex:team", "members": {"Person": [ALICE, "ex:bob"]}},
            {
                (EX.team, EX.members, EX.alice, DEFAULT),
                (EX.team, EX.members, EX.bob, DEFAULT),
                (EX.alice, RDF.type, EX.Person, DEFAULT),
                (EX.alice, EX.name, Literal("Alice"), DEFAULT),
                (EX.bob, RDF.type, EX.Person, DEFAULT),
            },
            id="type-map-array-property",
        ),
        pytest.param(
            {
                "@id": "ex:team",
                "byId": {"ex:carol": [{"name": "Carol"}, {"name": "Caroline"}]},
            },
            {
                (EX.team, EX.byId, EX.carol, DEFAULT),
                (EX.carol, EX.name, Literal("Carol"), DEFAULT),
                (EX.carol, EX.name, Literal("Caroline"), DEFAULT),
            },
            id="id-map-array",
        ),
        pytest.param(
            {"@id": "ex:team", "graphsById": {"ex:g": [ALICE, BOB]}},
            {
                (EX.team, EX.graphsById, EX.g, DEFAULT),
                (EX.alice, EX.name, Literal("Alice"), EX.g),
                (EX.bob, EX.name, Literal("Bob"), EX.g),
            },
            id="graph-id-map-array",
        ),
    ],
)
def test_map_value_array(data: dict[str, Any], expected: set[tuple]) -> None:
    assert set(_parse_jsonld(data).quads()) == expected


@pytest.mark.parametrize(
    ["term", "key"],
    [
        pytest.param("graphsByIndex", "g", id="graph-index"),
        pytest.param("graphsByIndex", "@none", id="graph-index-none"),
        pytest.param("graphsById", "@none", id="graph-id-none"),
    ],
)
@pytest.mark.parametrize(
    "values",
    [
        pytest.param([ALICE], id="node"),
        pytest.param([ALICE, None], id="trailing-null"),
        pytest.param([None, ALICE], id="leading-null"),
        pytest.param([None, ALICE, None], id="surrounding-nulls"),
        pytest.param([None], id="only-null"),
        pytest.param([], id="empty"),
    ],
)
def test_graph_map_null_array_items(
    term: str, key: str, values: list[dict[str, str] | None]
) -> None:
    ds = _parse_jsonld({"@id": "ex:team", term: {key: values}})
    if ALICE not in values:
        assert set(ds.quads()) == set()
        return

    (graph_id,) = ds.default_graph.objects(EX.team, EX[term])
    assert isinstance(graph_id, BNode)
    assert set(ds.quads()) == {
        (EX.team, EX[term], graph_id, DEFAULT),
        (EX.alice, EX.name, Literal("Alice"), graph_id),
    }


@pytest.mark.parametrize("key", ["g", "@none"])
@pytest.mark.parametrize("include_null", [False, True])
def test_graph_index_array_items_have_separate_graphs(
    key: str, include_null: bool
) -> None:
    values = [ALICE, None, BOB] if include_null else [ALICE, BOB]
    ds = _parse_jsonld({"@id": "ex:team", "graphsByIndex": {key: values}})
    (alice_quad,) = ds.quads((EX.alice, EX.name, Literal("Alice"), None))
    (bob_quad,) = ds.quads((EX.bob, EX.name, Literal("Bob"), None))
    alice_graph = alice_quad[3]
    bob_graph = bob_quad[3]
    assert isinstance(alice_graph, BNode)
    assert isinstance(bob_graph, BNode)
    assert alice_graph != bob_graph
    assert set(ds.quads()) == {
        (EX.team, EX.graphsByIndex, alice_graph, DEFAULT),
        (EX.team, EX.graphsByIndex, bob_graph, DEFAULT),
        (EX.alice, EX.name, Literal("Alice"), alice_graph),
        (EX.bob, EX.name, Literal("Bob"), bob_graph),
    }
