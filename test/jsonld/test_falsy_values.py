"""
The JSON-LD serializer joins a further value for a property to the value it
has already written. Whether one is present is a question about the key, not
about the truth of the value: with an active context ``0``, ``0.0``, ``""``
and ``false`` are written as bare JSON values, and testing them for truth made
the next value for the same property replace them, so one triple was lost.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any

import pytest

from rdflib import XSD, Dataset, Graph, Literal, Namespace
from rdflib.compare import isomorphic
from rdflib.term import Node

NS = Namespace("http://example.org/ns/")
VOCAB_CONTEXT = {"@vocab": str(NS)}
LANGUAGE_MAP_CONTEXT = {"p": {"@id": str(NS.p), "@container": "@language"}}
LANGUAGE_SET_CONTEXT = {"p": {"@id": str(NS.p), "@container": ["@language", "@set"]}}

FALSY_VALUES = [Literal(0), Literal(0.0), Literal(""), Literal(False)]
FALSY_IDS = ["0", "0.0", "empty-string", "false"]


def _graph(values: Sequence[Node]) -> Graph:
    g = Graph()
    for value in values:
        g.add((NS.s, NS.p, value))
    return g


def _round_trip(
    g: Graph, context: dict[str, Any] | None
) -> tuple[dict[str, Any], Graph]:
    data = g.serialize(format="json-ld", context=context)
    g2 = Graph()
    g2.parse(data=data, format="json-ld")
    return json.loads(data), g2


@pytest.mark.parametrize("falsy", FALSY_VALUES, ids=FALSY_IDS)
@pytest.mark.parametrize(
    "falsy_first", [True, False], ids=["falsy-first", "falsy-second"]
)
def test_a_falsy_value_beside_another_value_round_trips(
    falsy: Literal, falsy_first: bool
) -> None:
    """The falsy value was lost when the store yielded it first."""
    other = Literal("a")
    g = _graph([falsy, other] if falsy_first else [other, falsy])

    doc, g2 = _round_trip(g, VOCAB_CONTEXT)

    # Compared as JSON text, so that 0, 0.0, false and "" stay apart.
    assert sorted(map(json.dumps, doc["p"])) == sorted(
        map(json.dumps, [falsy.toPython(), "a"])
    )
    assert isomorphic(g, g2)


@pytest.mark.parametrize(
    ("datatype", "falsy", "other"),
    [(XSD.integer, "0", "1"), (XSD.boolean, "false", "true")],
    ids=["integer", "boolean"],
)
def test_a_falsy_value_under_a_typed_term_round_trips(
    datatype: str, falsy: str, other: str
) -> None:
    """Under a typed term the value is the literal itself, falsy as well."""
    context = {"n": {"@id": str(NS.p), "@type": str(datatype)}}
    g = _graph([Literal(falsy, datatype=datatype), Literal(other, datatype=datatype)])

    doc, g2 = _round_trip(g, context)

    assert sorted(doc["n"]) == sorted([falsy, other])
    assert isomorphic(g, g2)


def test_an_empty_string_under_a_language_term_round_trips() -> None:
    context = {"p": {"@id": str(NS.p), "@language": "en"}}
    g = _graph([Literal("", lang="en"), Literal("a", lang="en")])

    doc, g2 = _round_trip(g, context)

    assert sorted(doc["p"]) == ["", "a"]
    assert isomorphic(g, g2)


@pytest.mark.parametrize(
    "falsy_first", [True, False], ids=["falsy-first", "falsy-second"]
)
def test_an_empty_string_in_a_language_map_round_trips(falsy_first: bool) -> None:
    values = [Literal("", lang="en"), Literal("a", lang="en")]
    g = _graph(values if falsy_first else values[::-1])

    doc, g2 = _round_trip(g, LANGUAGE_MAP_CONTEXT)

    assert sorted(doc["p"]["en"]) == ["", "a"]
    assert isomorphic(g, g2)


def test_a_language_set_starts_without_a_null() -> None:
    """The same test turned a missing entry into ``[None]`` before appending."""
    g = _graph([Literal("a", lang="en")])

    doc, g2 = _round_trip(g, LANGUAGE_SET_CONTEXT)

    assert doc["p"] == {"en": ["a"]}
    assert isomorphic(g, g2)


@pytest.mark.parametrize(
    "context", [None, {"@base": str(NS.g)}], ids=["no-context", "base-context"]
)
def test_a_graph_named_by_the_base_iri_keeps_its_name(
    context: dict[str, Any] | None,
) -> None:
    """The graph name shrinks to ``""`` against the base, and was tested for truth."""
    ds = Dataset()
    ds.graph(NS.g).add((NS.s, NS.p, Literal("named")))
    ds.default_graph.add((NS.d, NS.p, Literal("default")))

    data = ds.serialize(format="json-ld", base=str(NS.g), context=context)
    ds2 = Dataset()
    ds2.parse(data=data, format="json-ld", base=str(NS.g))

    doc = json.loads(data)
    objects = doc["@graph"] if isinstance(doc, dict) else doc
    assert any(obj.get("@id") == "" and "@graph" in obj for obj in objects)
    assert (NS.s, NS.p, Literal("named")) in ds2.graph(NS.g)
    assert (NS.d, NS.p, Literal("default")) in ds2.default_graph


def test_several_falsy_values_beside_another_value_round_trip() -> None:
    g = _graph([Literal(0), Literal(""), Literal("a")])

    doc, g2 = _round_trip(g, VOCAB_CONTEXT)

    assert sorted(doc["p"], key=str) == ["", 0, "a"]
    assert isomorphic(g, g2)


def test_a_reference_equal_to_the_base_beside_another_round_trips() -> None:
    """A coerced IRI that shrinks to ``""`` is a value like any other."""
    context = {"ref": {"@id": str(NS.p), "@type": "@id"}}
    g = _graph([NS.s, NS.o])

    data = g.serialize(format="json-ld", context=context, base=str(NS.s))
    g2 = Graph()
    g2.parse(data=data, format="json-ld", base=str(NS.s))

    assert sorted(json.loads(data)["ref"]) == ["", "/ns/o"]
    assert isomorphic(g, g2)


@pytest.mark.parametrize("falsy", FALSY_VALUES, ids=FALSY_IDS)
def test_a_falsy_value_without_a_context_round_trips(falsy: Literal) -> None:
    """Guard: without a context every value is written as an object, which
    is never falsy, so this already round-tripped."""
    g = _graph([falsy, Literal("a")])

    _doc, g2 = _round_trip(g, None)

    assert isomorphic(g, g2)
