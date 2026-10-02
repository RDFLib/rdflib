"""WGS DefinedNamespace must use the vocabulary's http namespace IRI.

https://github.com/RDFLib/rdflib/issues/3529
"""

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import WGS

WGS84_NS = "http://www.w3.org/2003/01/geo/wgs84_pos#"


def test_wgs_namespace_iri_is_http():
    assert str(WGS) == WGS84_NS
    assert WGS.lat == URIRef(WGS84_NS + "lat")


def test_wgs_matches_published_data():
    g = Graph()
    g.parse(
        data="""
        @prefix wgs: <http://www.w3.org/2003/01/geo/wgs84_pos#> .
        <https://example.org/Chamonix> wgs:lat "45.92" .
        """,
        format="turtle",
    )
    assert g.value(URIRef("https://example.org/Chamonix"), WGS.lat) == Literal("45.92")


def test_wgs_prefix_used_on_serialize():
    g = Graph()
    g.parse(
        data="""
        @prefix wgs: <http://www.w3.org/2003/01/geo/wgs84_pos#> .
        <https://example.org/Chamonix> wgs:lat "45.92" .
        """,
        format="turtle",
    )
    ttl = g.serialize(format="turtle")
    assert "@prefix wgs: <http://www.w3.org/2003/01/geo/wgs84_pos#>" in ttl
    assert "wgs1:" not in ttl
