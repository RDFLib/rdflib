"""
JSON-LD 1.1 type, id and graph id maps whose entry values are arrays of node
objects, see https://github.com/RDFLib/rdflib/issues/3538.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from rdflib import RDF, Dataset, Literal, Namespace
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
