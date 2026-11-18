from __future__ import annotations

import json
from typing import Any

import pytest

from rdflib import OWL, RDF, Graph, Literal, Namespace, URIRef
from rdflib.plugins.shared.jsonld.errors import JSONLDException


def _parse_jsonld(doc: object) -> Graph:
    return Graph().parse(data=json.dumps(doc), format="json-ld")


def test_issue_1950_node_object_as_type_rejected() -> None:
    doc = {
        "@context": {
            "kb": "http://example.org/kb/",
            "owl": "http://www.w3.org/2002/07/owl#",
        },
        "@graph": {
            "@id": "kb:individual-a",
            "@type": {
                "@id": "http://example.org/ontology/core/MyClassA",
                "@type": "owl:Class",
            },
        },
    }
    with pytest.raises(JSONLDException, match="invalid type value"):
        _parse_jsonld(doc)


@pytest.mark.parametrize(
    "bad_type",
    [
        True,
        123,
        None,
        [{"@id": "http://example.org/A"}],
        ["http://example.org/A", 42],
    ],
)
def test_non_string_node_type_values_rejected(bad_type: Any) -> None:
    doc = {
        "@id": "http://example.org/s",
        "@type": bad_type,
    }
    with pytest.raises(JSONLDException, match="invalid type value"):
        _parse_jsonld(doc)


def test_top_level_and_aliased_invalid_type_rejected() -> None:
    with pytest.raises(JSONLDException, match="invalid type value"):
        _parse_jsonld({"@type": True})

    aliased_doc = {
        "@context": {"type": "@type"},
        "@id": "http://example.org/s",
        "type": {"@id": "http://example.org/ClassA"},
    }
    with pytest.raises(JSONLDException, match="invalid type value"):
        _parse_jsonld(aliased_doc)


@pytest.mark.parametrize(
    "bad_value_type",
    [
        {"@id": "http://example.org/dt"},
        False,
        None,
        ["http://example.org/dt"],
    ],
)
def test_value_object_invalid_type_rejected(bad_value_type: Any) -> None:
    doc = {
        "@id": "http://example.org/s",
        "http://example.org/p": {"@value": "abc", "@type": bad_value_type},
    }
    with pytest.raises(JSONLDException, match="invalid type value"):
        _parse_jsonld(doc)


def test_valid_string_and_list_types_and_null_context_coercion() -> None:
    kb = Namespace("http://example.org/kb/")
    doc = {
        "@context": {
            "kb": str(kb),
            "owl": str(OWL),
            "label": {"@id": "http://example.org/label", "@type": None},
        },
        "@graph": [
            {
                "@id": "kb:a",
                "@type": "owl:Class",
                "label": "hello",
            },
            {
                "@id": "kb:b",
                "@type": ["owl:Class", "kb:Thing"],
            },
            {
                "@id": "kb:c",
                "@type": [],
                "label": "empty-type-list",
            },
        ],
    }

    g = _parse_jsonld(doc)
    assert (kb.a, RDF.type, OWL.Class) in g
    assert (kb.a, URIRef("http://example.org/label"), Literal("hello")) in g
    assert (kb.b, RDF.type, OWL.Class) in g
    assert (kb.b, RDF.type, kb.Thing) in g
    assert (kb.c, URIRef("http://example.org/label"), Literal("empty-type-list")) in g
