"""
A term with ``"@type": "@id"`` or ``"@type": "@vocab"`` fits a list of node
references only.

The serializer wrote any list under such a term, whatever its members. A
literal member was written as a bare string, and parsing read it back as an
IRI: ``"x"`` became ``<http://base.example/x>`` under ``@id`` and
``<http://example.org/ns/x>`` under ``@vocab``. A list with a literal member,
or with a nested list, now goes under an ``@list`` term without a type, under
the plain term for the property, or under the property IRI.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any

import pytest

from rdflib import BNode, Graph, Literal, Namespace
from rdflib.collection import Collection
from rdflib.compare import isomorphic
from rdflib.term import Node

NS = Namespace("http://example.org/ns/")
BASE = "http://base.example/"
ID_LIST_CONTEXT = {
    "items": {"@id": str(NS.items), "@container": "@list", "@type": "@id"}
}
VOCAB_LIST_CONTEXT = {
    "@vocab": str(NS),
    "items": {"@id": str(NS.items), "@container": "@list", "@type": "@vocab"},
}
# A term without @list: a list is written under it as a list object.
VOCAB_TERM_CONTEXT = {
    "@vocab": str(NS),
    "ref": {"@id": str(NS.items), "@type": "@vocab"},
}
# Each coercing context, with the key the property IRI compacts to there.
COERCING_CONTEXTS = [
    pytest.param(ID_LIST_CONTEXT, str(NS.items), id="id-list-term"),
    pytest.param(VOCAB_LIST_CONTEXT, str(NS.items), id="vocab-list-term"),
    pytest.param(VOCAB_TERM_CONTEXT, "items", id="vocab-term"),
]
LITERALS = [Literal("x"), Literal(2)]


def _list_graph(members: Sequence[Node]) -> Graph:
    g = Graph()
    head = BNode()
    Collection(g, head, list(members))
    g.add((NS.s, NS.items, head))
    return g


def _nested_list_graph(inner_members: Sequence[Node]) -> Graph:
    g = Graph()
    inner, outer = BNode(), BNode()
    Collection(g, inner, list(inner_members))
    Collection(g, outer, [inner])
    g.add((NS.s, NS.items, outer))
    return g


def _round_trip(g: Graph, context: dict[str, Any]) -> tuple[dict[str, Any], Graph]:
    data = g.serialize(format="json-ld", context=context)
    g2 = Graph()
    g2.parse(data=data, format="json-ld", base=BASE)
    return json.loads(data), g2


@pytest.mark.parametrize(("context", "iri_key"), COERCING_CONTEXTS)
@pytest.mark.parametrize(
    "members",
    [LITERALS, [NS.a, Literal("x")]],
    ids=["literals", "node-and-literal"],
)
def test_a_list_with_a_literal_member_round_trips(
    context: dict[str, Any], iri_key: str, members: Sequence[Node]
) -> None:
    g = _list_graph(members)

    _doc, g2 = _round_trip(g, context)

    assert isomorphic(g, g2)


@pytest.mark.parametrize(("context", "iri_key"), COERCING_CONTEXTS)
def test_a_list_with_a_literal_member_is_a_list_object_under_the_iri(
    context: dict[str, Any], iri_key: str
) -> None:
    g = _list_graph(LITERALS)

    doc, _g2 = _round_trip(g, context)

    assert "ref" not in doc
    assert doc[iri_key] == {"@list": ["x", 2]}


@pytest.mark.parametrize(("context", "iri_key"), COERCING_CONTEXTS)
def test_a_nested_list_round_trips(context: dict[str, Any], iri_key: str) -> None:
    """Under ``@vocab`` the literal members of the nested list would take the
    coercion; under ``@id`` the nested list would be a reference to explicit
    cells. It is written inline under the IRI instead."""
    g = _nested_list_graph(LITERALS)

    doc, g2 = _round_trip(g, context)

    assert doc[iri_key] == {"@list": [{"@list": ["x", 2]}]}
    assert isomorphic(g, g2)


def test_a_list_with_a_literal_member_uses_an_untyped_list_term() -> None:
    context = {**ID_LIST_CONTEXT, "list": {"@id": str(NS.items), "@container": "@list"}}
    g = _list_graph(LITERALS)

    doc, g2 = _round_trip(g, context)

    assert "items" not in doc
    assert doc["list"] == ["x", 2]
    assert isomorphic(g, g2)


def test_a_list_with_a_literal_member_uses_the_plain_term() -> None:
    context = {**ID_LIST_CONTEXT, "item": {"@id": str(NS.items)}}
    g = _list_graph(LITERALS)

    doc, g2 = _round_trip(g, context)

    assert "items" not in doc
    assert doc["item"] == {"@list": ["x", 2]}
    assert isomorphic(g, g2)


@pytest.mark.parametrize(
    "plain_term",
    [{"@type": "@id"}, {"@type": "@vocab"}],
    ids=["id-typed", "vocab-typed"],
)
def test_a_list_with_a_literal_member_skips_a_coercing_plain_term(
    plain_term: dict[str, str],
) -> None:
    """With no term that fits, the list goes under the IRI, not under a
    coercing term without ``@list``."""
    context = {
        "@vocab": str(NS),
        **ID_LIST_CONTEXT,
        "ref": {"@id": str(NS.items), **plain_term},
    }
    g = _list_graph(LITERALS)

    doc, g2 = _round_trip(g, context)

    assert "ref" not in doc
    assert doc[str(NS.items)] == {"@list": ["x", 2]}
    assert isomorphic(g, g2)


@pytest.mark.parametrize(
    "context", [ID_LIST_CONTEXT, VOCAB_LIST_CONTEXT], ids=["id", "vocab"]
)
def test_a_list_of_node_references_still_uses_the_coercing_list_term(
    context: dict[str, Any],
) -> None:
    """Guard: the coercing ``@list`` term still fits node references."""
    g = _list_graph([NS.a, NS.b])

    doc, g2 = _round_trip(g, context)

    assert len(doc["items"]) == 2
    assert all(isinstance(member, str) for member in doc["items"])
    assert isomorphic(g, g2)


def test_a_list_of_node_references_stays_under_a_vocab_term() -> None:
    """Guard: a list object of node references is read back unchanged under
    a coercing term without ``@list``, so it stays there."""
    g = _list_graph([NS.a, NS.b])

    doc, g2 = _round_trip(g, VOCAB_TERM_CONTEXT)

    assert doc["ref"] == {"@list": [{"@id": str(NS.a)}, {"@id": str(NS.b)}]}
    assert isomorphic(g, g2)


@pytest.mark.parametrize(
    "context", [ID_LIST_CONTEXT, VOCAB_LIST_CONTEXT], ids=["id", "vocab"]
)
def test_blank_node_members_under_a_coercing_list_term_round_trip(
    context: dict[str, Any],
) -> None:
    """Guard: blank nodes are node references, and a described member keeps
    its description."""
    described, bare = BNode(), BNode()
    g = _list_graph([described, bare])
    g.add((described, NS.p, Literal("x")))

    doc, g2 = _round_trip(g, context)

    (node,) = (n for n in doc["@graph"] if n["@id"] == str(NS.s))
    assert len(node["items"]) == 2
    assert described.n3() in {n["@id"] for n in doc["@graph"]}
    assert isomorphic(g, g2)
