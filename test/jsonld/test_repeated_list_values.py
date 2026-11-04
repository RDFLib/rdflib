"""
A term with ``"@container": "@list"`` holds one list: its value *is* the list.

A subject with more than one ``rdf:List`` value for such a property had each
later list appended to the first list's array. JSON-LD reads a nested array in
a list as a list of lists, so ``s items ("a")`` and ``s items ("b")`` came
back as ``s items ("a" ("b"))``. The first list keeps the term; every further
list is written as a list object under a plain term for the property, or under
the property IRI or compact IRI when there is none.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any

import pytest

from rdflib import BNode, Dataset, Graph, Literal, Namespace
from rdflib.collection import Collection
from rdflib.compare import isomorphic
from rdflib.term import Node

NS = Namespace("http://example.org/ns/")
LIST_CONTEXT = {"items": {"@id": str(NS.items), "@container": "@list"}}
COERCING_LIST_CONTEXT = {
    "items": {"@id": str(NS.items), "@container": "@list", "@type": "@id"}
}
# The plain term is the one a node object gets; the list term is preferred
# for a list of node references.
TWO_TERM_CONTEXT = {**COERCING_LIST_CONTEXT, "item": {"@id": str(NS.items)}}
LITERALS = [Literal("a"), Literal("b"), Literal("c")]
IRIS = [NS.a, NS.b, NS.c]


def _graph_with_lists(
    members: Sequence[Node], count: int, g: Graph | None = None
) -> Graph:
    """``ns:s ns:items`` with ``count`` single-member lists."""
    if g is None:
        g = Graph()
    for member in members[:count]:
        head = BNode()
        Collection(g, head, [member])
        g.add((NS.s, NS.items, head))
    return g


def _round_trip(g: Graph, context: dict[str, Any]) -> tuple[dict[str, Any], Graph]:
    data = g.serialize(format="json-ld", context=context)
    g2 = Graph()
    g2.parse(data=data, format="json-ld")
    return json.loads(data), g2


@pytest.mark.parametrize("count", [2, 3])
@pytest.mark.parametrize(
    ("context", "members"),
    [
        (LIST_CONTEXT, LITERALS),
        (COERCING_LIST_CONTEXT, IRIS),
        (TWO_TERM_CONTEXT, IRIS),
    ],
    ids=["list-term", "coercing-list-term", "list-and-plain-term"],
)
def test_several_lists_under_a_list_container_term_round_trip(
    context: dict[str, Any], members: Sequence[Node], count: int
) -> None:
    g = _graph_with_lists(members, count)

    _doc, g2 = _round_trip(g, context)

    assert isomorphic(g, g2)


def test_a_further_list_goes_under_the_term_without_list() -> None:
    g = _graph_with_lists(IRIS, 2)

    doc, _g2 = _round_trip(g, TWO_TERM_CONTEXT)

    assert doc["items"] in ([str(NS.a)], [str(NS.b)])
    other = str(NS.b) if doc["items"] == [str(NS.a)] else str(NS.a)
    assert doc["item"] == {"@list": [{"@id": other}]}


def test_a_further_list_goes_under_the_iri_when_there_is_no_other_term() -> None:
    g = _graph_with_lists(LITERALS, 2)

    doc, _g2 = _round_trip(g, LIST_CONTEXT)

    assert doc["items"] in (["a"], ["b"])
    other = "b" if doc["items"] == ["a"] else "a"
    assert doc[str(NS.items)] == {"@list": [other]}


def test_a_further_list_goes_under_the_iri_beside_a_coercing_term() -> None:
    """A coercing term would write a reference, not a list object."""
    context = {**COERCING_LIST_CONTEXT, "ref": {"@id": str(NS.items), "@type": "@id"}}
    g = _graph_with_lists(IRIS, 2)

    doc, g2 = _round_trip(g, context)

    assert doc["items"] in ([str(NS.a)], [str(NS.b)])
    other = str(NS.b) if doc["items"] == [str(NS.a)] else str(NS.a)
    assert doc[str(NS.items)] == {"@list": [{"@id": other}]}
    assert "ref" not in doc
    assert isomorphic(g, g2)


@pytest.mark.parametrize("container", ["@index", "@id", "@type", "@graph"])
def test_a_further_list_goes_under_the_iri_beside_a_map_container_term(
    container: str,
) -> None:
    """A map container term would read the list object as a map."""
    context = {
        **COERCING_LIST_CONTEXT,
        "map": {"@id": str(NS.items), "@container": container},
    }
    g = _graph_with_lists(IRIS, 2)

    doc, g2 = _round_trip(g, context)

    assert doc["items"] in ([str(NS.a)], [str(NS.b)])
    other = str(NS.b) if doc["items"] == [str(NS.a)] else str(NS.a)
    assert doc[str(NS.items)] == {"@list": [{"@id": other}]}
    assert "map" not in doc
    assert isomorphic(g, g2)


def test_a_further_list_goes_under_a_set_term() -> None:
    context = {
        **COERCING_LIST_CONTEXT,
        "item": {"@id": str(NS.items), "@container": "@set"},
    }
    g = _graph_with_lists(IRIS, 2)

    doc, g2 = _round_trip(g, context)

    assert doc["items"] in ([str(NS.a)], [str(NS.b)])
    other = str(NS.b) if doc["items"] == [str(NS.a)] else str(NS.a)
    assert doc["item"] == [{"@list": [{"@id": other}]}]
    assert isomorphic(g, g2)


def test_a_further_list_goes_under_a_compact_iri() -> None:
    context = {**LIST_CONTEXT, "ns": str(NS)}
    g = _graph_with_lists(LITERALS, 2)

    doc, g2 = _round_trip(g, context)

    assert doc["items"] in (["a"], ["b"])
    other = "b" if doc["items"] == ["a"] else "a"
    assert doc["ns:items"] == {"@list": [other]}
    assert isomorphic(g, g2)


def test_several_lists_in_a_named_graph_round_trip() -> None:
    ds = Dataset()
    _graph_with_lists(LITERALS, 2, ds.graph(NS.g))

    data = ds.serialize(format="json-ld", context=LIST_CONTEXT)
    ds2 = Dataset()
    ds2.parse(data=data, format="json-ld")

    assert isomorphic(ds.graph(NS.g), ds2.graph(NS.g))


def test_a_single_list_still_uses_the_list_container_term() -> None:
    g = _graph_with_lists(LITERALS, 1)

    doc, g2 = _round_trip(g, LIST_CONTEXT)

    assert doc["items"] == ["a"]
    assert isomorphic(g, g2)


def test_a_list_beside_a_non_list_value_round_trips() -> None:
    g = _graph_with_lists(LITERALS, 1)
    g.add((NS.s, NS.items, NS.x))

    doc, g2 = _round_trip(g, LIST_CONTEXT)

    assert doc["items"] == ["a"]
    assert isomorphic(g, g2)
