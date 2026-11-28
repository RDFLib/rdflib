"""
A string that is a keyword, or has the form of one, is not an IRI. IRI
expansion returns a keyword as is and drops a keyword-shaped string (JSON-LD
1.1 API, section 5.2.2, steps 1 and 2), so a ``@type`` value or a value of a
term with ``"@type": "@vocab"`` that is such a string makes no triple. The
parser used to expand it against ``@vocab`` and add, for example,
``<Georgia> rdf:type <vocab#@id>`` (issue #2168).
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from rdflib import RDF, Graph, Namespace, URIRef

BASE = Namespace("https://examples.r.us/")
VOCAB = Namespace("https://examples.r.us/vocab#")
CONTEXT = {"@base": str(BASE), "@vocab": str(VOCAB)}


def _parse(doc: dict[str, Any]) -> set[tuple[Any, Any, Any]]:
    g = Graph()
    g.parse(data=json.dumps(doc), format="json-ld")
    return set(g)


def test_issue_2168_type_id_on_a_node_object_adds_no_type() -> None:
    doc = {
        "@context": CONTEXT,
        "@id": "Subject",
        "loc": {"@id": "Georgia", "@type": "@id"},
    }
    assert _parse(doc) == {(BASE.Subject, VOCAB.loc, BASE.Georgia)}


@pytest.mark.parametrize("keyword", ["@id", "@context", "@foo"])
def test_keyword_type_value_adds_no_type(keyword: str) -> None:
    doc = {"@context": CONTEXT, "@id": "S", "@type": ["Thing", keyword]}
    assert _parse(doc) == {(BASE.S, RDF.type, VOCAB.Thing)}


def test_keyword_value_of_a_vocab_typed_term_adds_no_triple() -> None:
    doc = {
        "@context": {**CONTEXT, "p": {"@type": "@vocab"}},
        "@id": "S",
        "p": ["@id", "Thing"],
    }
    assert _parse(doc) == {(BASE.S, VOCAB.p, VOCAB.Thing)}


@pytest.mark.parametrize("value", ["@", "email@example"])
def test_strings_that_are_not_keyword_shaped_still_expand(value: str) -> None:
    doc = {"@context": CONTEXT, "@id": "S", "@type": value}
    assert _parse(doc) == {(BASE.S, RDF.type, URIRef(VOCAB + value))}
