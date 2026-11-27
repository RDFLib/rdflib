from __future__ import annotations

from rdflib import Graph, Literal, URIRef
from rdflib.plugins.sparql import prepareQuery
from rdflib.plugins.sparql.algebra import translateUpdate
from rdflib.plugins.sparql.parser import parseUpdate


def test_translate_update_with_urn_base() -> None:
    upd_str = (
        "DELETE {} INSERT {<#h1> <http://ex.org/ns/p1> <http:ex.org/ns/o1> } WHERE {}"
    )
    translated = translateUpdate(parseUpdate(upd_str), URIRef("urn:ns:a"))
    inserted_triples = translated.algebra[0]["insert"]["triples"]
    assert inserted_triples == [
        (
            URIRef("urn:ns:a#h1"),
            URIRef("http://ex.org/ns/p1"),
            URIRef("http:ex.org/ns/o1"),
        )
    ]


def test_sparql_query_and_update_with_non_http_base() -> None:
    g = Graph()
    g.update('BASE <urn:ns:a> INSERT DATA { <#h1> <urn:ns:p> "v" }')
    assert (URIRef("urn:ns:a#h1"), URIRef("urn:ns:p"), Literal("v")) in g

    prepared = prepareQuery("BASE <urn:ns:a> SELECT ?p ?o WHERE { <#h1> ?p ?o }")
    assert prepared.prologue.base == URIRef("urn:ns:a")
    assert list(g.query(prepared)) == [(URIRef("urn:ns:p"), Literal("v"))]


def test_translate_update_tag_and_http_bases() -> None:
    tag_upd = translateUpdate(
        parseUpdate('INSERT DATA { <#sec1> <urn:ns:p> "v" }'),
        "tag:example.org,2020:doc",
    )
    assert tag_upd.algebra[0]["triples"][0][0] == URIRef(
        "tag:example.org,2020:doc#sec1"
    )

    http_upd = translateUpdate(
        parseUpdate('INSERT DATA { <#h1> <urn:ns:p> "v" }'),
        URIRef("http://ex.org/gr/a"),
    )
    assert http_upd.algebra[0]["triples"][0][0] == URIRef("http://ex.org/gr/a#h1")
