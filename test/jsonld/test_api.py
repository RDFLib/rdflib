# -*- coding: UTF-8 -*-
import pytest
from rdflib.plugin import register, Parser, Serializer

register("json-ld", Parser, "rdflib.plugins.parsers.jsonld", "JsonLDParser")
register("json-ld", Serializer, "rdflib.plugins.serializers.jsonld", "JsonLDSerializer")

from rdflib import Graph, Dataset, Literal, URIRef

test_json = """
{
    "@context": {
        "dc": "http://purl.org/dc/terms/",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
    },
    "@id": "http://example.org/about",
    "dc:title": {
        "@language": "en",
        "@value": "Someone's Homepage"
    }
}
"""

triples_list = [
    (
        URIRef("http://example.org/about"),
        URIRef("http://purl.org/dc/terms/title"),
        Literal("Someone's Homepage", lang="en"),
    )
]


@pytest.mark.xfail(reason="Parsing JSON-LD into a Graph")
def test_parse_graph():
    test_json = """
    {
        "@context": {
            "dc": "http://purl.org/dc/terms/",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
        },
        "@id": "http://example.org/about",
        "dc:title": {
            "@language": "en",
            "@value": "Someone's Homepage"
        }
    }
    """
    g = Graph().parse(data=test_json, format="json-ld")
    assert list(g) == triples_list


def test_parse_dataset():
    g = Dataset().parse(data=test_json, format="json-ld")

    assert list(g.default_graph) == triples_list
