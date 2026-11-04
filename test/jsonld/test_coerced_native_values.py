"""
A type mapping of ``@id`` or ``@vocab`` applies to strings only, and ``@none``
applies no type at all (Value Expansion, JSON-LD 1.1 Processing Algorithms and
API, section 5.3.2). A number or boolean under such a term is a value object
without ``@type``, so it keeps the datatype its JSON type implies.

The parser copied the keyword into ``@type`` instead. Under ``@vocab`` the
keyword expanded to the empty string, so ``2`` became a literal with the empty
IRI as datatype: equal to neither ``2`` nor ``"2"``, and written by N-Triples
as the plain string ``"2"``.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from rdflib import RDF, XSD, Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.plugins.parsers.jsonld import Parser
from rdflib.plugins.shared.jsonld.context import Context

NS = Namespace("http://example.org/ns/")
KEYWORD_TYPES = ["@id", "@vocab", "@none"]
NATIVE_VALUES = [
    pytest.param(2, Literal(2), id="integer"),
    pytest.param(2.5, Literal(2.5), id="double"),
    pytest.param(True, Literal(True), id="true"),
    pytest.param(False, Literal(False), id="false"),
]


def _parse(context: dict[str, Any], value: Any) -> Graph:
    # With a vocabulary, the keyword copied into @type expanded to an IRI
    # under @none as well; without one it expanded to None and hid the bug.
    doc = {"@context": {"@vocab": str(NS), **context}, "@id": str(NS.s), "p": value}
    g = Graph()
    g.parse(data=json.dumps(doc), format="json-ld")
    return g


def _term(**mapping: Any) -> dict[str, Any]:
    return {"@id": str(NS.p), **mapping}


@pytest.mark.parametrize("keyword", KEYWORD_TYPES)
@pytest.mark.parametrize(("value", "literal"), NATIVE_VALUES)
def test_a_native_value_under_a_keyword_typed_term_keeps_its_datatype(
    keyword: str, value: Any, literal: Literal
) -> None:
    g = _parse({"p": _term(**{"@type": keyword})}, value)

    (parsed,) = g.objects(NS.s, NS.p)
    assert parsed == literal


@pytest.mark.parametrize("keyword", KEYWORD_TYPES)
@pytest.mark.parametrize(("value", "literal"), NATIVE_VALUES)
def test_a_native_list_member_under_a_keyword_typed_term_keeps_its_datatype(
    keyword: str, value: Any, literal: Literal
) -> None:
    g = _parse({"p": _term(**{"@type": keyword, "@container": "@list"})}, [value])

    (head,) = g.objects(NS.s, NS.p)
    (parsed,) = Collection(g, head)
    assert parsed == literal


def test_a_string_under_a_none_typed_term_takes_the_default_language() -> None:
    """``@none`` leaves the value untyped, so the language applies to it."""
    g = _parse({"@language": "en", "p": _term(**{"@type": "@none"})}, "x")

    (parsed,) = g.objects(NS.s, NS.p)
    assert parsed == Literal("x", lang="en")


@pytest.mark.parametrize("term_language", ["de", None], ids=["de", "null"])
@pytest.mark.parametrize("default_language", [None, "fr"], ids=["no-default", "fr"])
def test_a_typed_term_has_no_language_mapping(
    term_language: str | None, default_language: str | None
) -> None:
    """Create Term Definition (section 4.2.2, step 22) sets a language mapping
    only for a term definition without ``@type``, so the default language
    applies, if there is one."""
    context: dict[str, Any] = {
        "p": _term(**{"@type": "@none", "@language": term_language})
    }
    if default_language:
        context["@language"] = default_language
    g = _parse(context, "x")

    (parsed,) = g.objects(NS.s, NS.p)
    assert parsed == Literal("x", lang=default_language)


def test_a_typed_term_added_through_the_api_has_no_language_mapping() -> None:
    """The rule holds for a term added with ``Context.add_term`` too."""
    context = Context()
    context.language = "fr"
    context.add_term("p", str(NS.p), coercion="@none", language="de")
    g = Graph()
    Parser().parse({"@id": str(NS.s), "p": "x"}, context, g)

    assert list(g.objects(NS.s, NS.p)) == [Literal("x", lang="fr")]


@pytest.mark.parametrize("term_language", ["de", None], ids=["de", "null"])
@pytest.mark.parametrize("default_language", [None, "fr"], ids=["no-default", "fr"])
def test_a_null_typed_term_keeps_its_language_mapping(
    term_language: str | None, default_language: str | None
) -> None:
    """Section 4.2.2 makes a null ``@type`` an invalid type mapping error.
    RDFLib accepts it as a term without a type mapping, so the term's own
    language mapping applies, as it did before."""
    context: dict[str, Any] = {
        "p": _term(**{"@type": None, "@language": term_language})
    }
    if default_language:
        context["@language"] = default_language
    g = _parse(context, "x")

    (parsed,) = g.objects(NS.s, NS.p)
    assert parsed == Literal("x", lang=term_language)


@pytest.mark.parametrize(
    ("keyword", "iri"),
    [("@id", URIRef("http://base.example/x")), ("@vocab", NS.x)],
)
def test_a_string_under_an_iri_typed_term_is_still_an_iri(
    keyword: str, iri: URIRef
) -> None:
    doc = {
        "@context": {"@vocab": str(NS), "p": _term(**{"@type": keyword})},
        "@id": str(NS.s),
        "p": "x",
    }
    g = Graph()
    g.parse(data=json.dumps(doc), format="json-ld", base="http://base.example/")

    assert list(g.objects(NS.s, NS.p)) == [iri]


def test_a_native_value_under_a_datatype_typed_term_is_still_typed() -> None:
    g = _parse({"p": _term(**{"@type": str(XSD.decimal)})}, 2)

    assert list(g.objects(NS.s, NS.p)) == [Literal("2", datatype=XSD.decimal)]


@pytest.mark.parametrize("keyword", KEYWORD_TYPES)
def test_a_null_under_a_keyword_typed_term_is_dropped(keyword: str) -> None:
    g = _parse({"p": _term(**{"@type": keyword})}, None)

    assert len(g) == 0


def test_a_null_under_a_json_typed_term_is_still_a_json_literal() -> None:
    g = _parse({"@version": 1.1, "p": _term(**{"@type": "@json"})}, None)

    assert list(g.objects(NS.s, NS.p)) == [Literal("null", datatype=RDF.JSON)]
