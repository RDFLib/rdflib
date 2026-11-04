"""
The JSON-LD serializer recognises an ``rdf:List`` cell by its entries, not by
the truth value of what they hold.

The Serialize RDF as JSON-LD Algorithm (JSON-LD 1.1 Processing Algorithms and
API, section 8.4) converts a chain to ``@list`` while each cell has an
``rdf:first`` and an ``rdf:rest`` entry with exactly one value each. The
serializer tested those values with Python truthiness instead, so a list
starting with ``0``, ``""`` or ``false`` was not written as ``@list``, and a
second ``rdf:first`` or ``rdf:rest`` on a cell replaced a falsy first one, which
dropped that triple from the output.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from rdflib import RDF, BNode, Graph, Literal, Namespace
from rdflib.collection import Collection
from rdflib.compare import isomorphic
from rdflib.plugins.serializers.jsonld import Converter
from rdflib.plugins.shared.jsonld.context import Context
from rdflib.term import Node

NS = Namespace("http://example.org/ns/")
LIST_CONTEXT = {"p": {"@id": str(NS.p), "@container": "@list"}}
COERCING_LIST_CONTEXT = {"p": {**LIST_CONTEXT["p"], "@type": "@id"}}
VOCAB_LIST_CONTEXT = {
    "@vocab": str(NS),
    "p": {**LIST_CONTEXT["p"], "@type": "@vocab"},
}

FALSY_MEMBERS = [Literal(0), Literal(0.0), Literal(""), Literal(False)]
FALSY_IDS = ["0", "0.0", "empty-string", "false"]


def _list_graph(members: list[Node]) -> tuple[Graph, BNode]:
    g = Graph()
    head = BNode()
    Collection(g, head, members)
    g.add((NS.s, NS.p, head))
    return g, head


def _two_cell_chain() -> tuple[Graph, BNode, BNode]:
    """``ns:s ns:p ( 1 ... )`` with the second cell left for the caller to fill."""
    g = Graph()
    head, cell = BNode(), BNode()
    g.add((NS.s, NS.p, head))
    g.add((head, RDF.first, Literal(1)))
    g.add((head, RDF.rest, cell))
    return g, head, cell


def _round_trip(g: Graph, context: dict[str, Any] | None = None) -> tuple[str, Graph]:
    data = g.serialize(format="json-ld", context=context)
    g2 = Graph()
    g2.parse(data=data, format="json-ld")
    return data, g2


@pytest.mark.parametrize("first", FALSY_MEMBERS, ids=FALSY_IDS)
def test_a_list_starting_with_a_falsy_member_is_written_as_a_list(
    first: Literal,
) -> None:
    g, _head = _list_graph([first, Literal("a")])

    data, g2 = _round_trip(g)

    assert str(RDF.first) not in data
    assert isomorphic(g, g2)


@pytest.mark.parametrize("first", FALSY_MEMBERS, ids=FALSY_IDS)
def test_a_list_starting_with_a_falsy_member_uses_a_list_container_term(
    first: Literal,
) -> None:
    g, _head = _list_graph([first, Literal("a")])

    data, g2 = _round_trip(g, LIST_CONTEXT)

    (member, _a) = json.loads(data)["p"]
    assert member == first.toPython() and type(member) is type(first.toPython())
    assert isomorphic(g, g2)


@pytest.mark.parametrize("first", FALSY_MEMBERS, ids=FALSY_IDS)
def test_a_list_starting_with_a_falsy_member_is_not_coerced(first: Literal) -> None:
    """Once recognised, the chain must not go under a term that coerces its
    members to IRIs. It is written as a list object under the IRI instead."""
    g, _head = _list_graph([first, Literal("a")])

    data, g2 = _round_trip(g, COERCING_LIST_CONTEXT)

    (member, _a) = json.loads(data)[str(NS.p)]["@list"]
    assert member == first.toPython() and type(member) is type(first.toPython())
    assert isomorphic(g, g2)


@pytest.mark.parametrize("first", FALSY_MEMBERS, ids=FALSY_IDS)
def test_a_nested_list_starting_with_a_falsy_member_round_trips(first: Literal) -> None:
    """Guard: once recognised, a nested list keeps the outer list off a term
    that coerces to ``@vocab``, which would turn its literals into IRIs."""
    g = Graph()
    inner, outer = BNode(), BNode()
    Collection(g, inner, [first, Literal("a")])
    Collection(g, outer, [inner])
    g.add((NS.s, NS.p, outer))

    _data, g2 = _round_trip(g, VOCAB_LIST_CONTEXT)

    assert isomorphic(g, g2)


@pytest.mark.parametrize("first", FALSY_MEMBERS, ids=FALSY_IDS)
def test_to_collection_returns_a_falsy_first_member(first: Literal) -> None:
    g, head = _list_graph([first, Literal("a")])
    converter = Converter(Context(), False, False)

    assert converter.to_collection(g, head) == [first, Literal("a")]


@pytest.mark.parametrize("extra", [Literal(0), Literal(5)], ids=["falsy", "truthy"])
def test_a_cell_with_two_rdf_first_values_is_not_a_list(extra: Node) -> None:
    """The second value replaced a falsy first one, and the chain stayed a list."""
    g, _head, cell = _two_cell_chain()
    g.add((cell, RDF.first, extra))
    g.add((cell, RDF.first, Literal(2)))
    g.add((cell, RDF.rest, RDF.nil))

    data, g2 = _round_trip(g)

    assert str(RDF.first) in data
    assert isomorphic(g, g2)


@pytest.mark.parametrize("extra", [Literal(""), NS.other], ids=["falsy", "truthy"])
def test_a_cell_with_two_rdf_rest_values_is_not_a_list(extra: Node) -> None:
    g, _head, cell = _two_cell_chain()
    g.add((cell, RDF.first, Literal(2)))
    g.add((cell, RDF.rest, extra))
    g.add((cell, RDF.rest, RDF.nil))

    data, g2 = _round_trip(g)

    assert str(RDF.first) in data
    assert isomorphic(g, g2)


def test_a_cell_without_rdf_first_is_not_a_list() -> None:
    """A missing entry left ``None`` in the member list and lost the cell."""
    g, _head, cell = _two_cell_chain()
    g.add((cell, RDF.rest, RDF.nil))

    data, g2 = _round_trip(g)

    assert str(RDF.first) in data
    assert isomorphic(g, g2)


def test_a_cell_without_rdf_rest_is_not_a_list() -> None:
    g, _head, cell = _two_cell_chain()
    g.add((cell, RDF.first, Literal(2)))

    data, g2 = _round_trip(g)

    assert str(RDF.first) in data
    assert isomorphic(g, g2)


def test_to_collection_rejects_a_cell_with_an_extra_or_missing_entry() -> None:
    """The decision itself, so the reason survives a refactor of the caller."""
    converter = Converter(Context(), False, False)

    duplicated, head, cell = _two_cell_chain()
    duplicated.add((cell, RDF.first, Literal(0)))
    duplicated.add((cell, RDF.first, Literal(2)))
    duplicated.add((cell, RDF.rest, RDF.nil))
    assert converter.to_collection(duplicated, head) is None

    missing, head, cell = _two_cell_chain()
    missing.add((cell, RDF.rest, RDF.nil))
    assert converter.to_collection(missing, head) is None


def test_a_coerced_list_member_equal_to_the_base_is_written_as_a_string() -> None:
    """A member IRI that shrinks to ``""`` is as coerced as any other."""
    g, _head = _list_graph([NS.s, NS.o])

    data = g.serialize(format="json-ld", context=COERCING_LIST_CONTEXT, base=str(NS.s))
    g2 = Graph()
    g2.parse(data=data, format="json-ld", base=str(NS.s))

    assert json.loads(data)["p"][0] == ""
    assert isomorphic(g, g2)


def test_a_typed_cell_is_still_a_list() -> None:
    """``rdf:type rdf:List`` on a cell is the one extra entry section 8.4 allows.

    The ``@list`` form implies that type, so the type triple is not written.
    """
    g, head = _list_graph([Literal(0), Literal("a")])
    g.add((head, RDF.type, RDF.List))

    data, g2 = _round_trip(g)

    assert str(RDF.first) not in data
    g.remove((head, RDF.type, RDF.List))
    assert isomorphic(g, g2)
