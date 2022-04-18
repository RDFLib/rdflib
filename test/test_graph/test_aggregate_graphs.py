from io import StringIO

from rdflib import logger, plugin
from rdflib.graph import ConjunctiveGraph, Graph, ReadOnlyGraphAggregate
from rdflib.namespace import RDF, RDFS
from rdflib.store import Store
from rdflib.term import URIRef

testGraph1N3 = """
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <http://test/> .
:foo a rdfs:Class.
:bar :d :c.
:a :d :c.
"""


testGraph2N3 = """
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <http://test/> .
@prefix log: <http://www.w3.org/2000/10/swap/log#>.
:foo a rdfs:Resource.
:bar rdfs:isDefinedBy [ a log:Formula ].
:a :d :e.
"""

testGraph3N3 = """
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix log: <http://www.w3.org/2000/10/swap/log#>.
@prefix : <http://test/> .
<> a log:N3Document.
"""

sparqlQ = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT *
FROM NAMED <http://example.com/graph1>
FROM NAMED <http://example.com/graph2>
FROM NAMED <http://example.com/graph3>
FROM <http://www.w3.org/2000/01/rdf-schema#>

WHERE {?sub ?pred rdfs:Class }"""

sparqlQ2 = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?class
WHERE { GRAPH ?graph { ?member a ?class } }"""

sparqlQ3 = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX log: <http://www.w3.org/2000/10/swap/log#>
SELECT ?n3Doc
WHERE {?n3Doc a log:N3Document }"""


def test_aggregate_raw():
    memStore = plugin.get("Memory", Store)()
    graph1 = Graph(memStore)
    graph2 = Graph(memStore)
    graph3 = Graph(memStore)

    for n3Str, graph in [
        (testGraph1N3, graph1),
        (testGraph2N3, graph2),
        (testGraph3N3, graph3),
    ]:
        graph.parse(StringIO(n3Str), format="n3")

    G = ReadOnlyGraphAggregate([graph1, graph2, graph3])

    # Test triples
    assert len(list(G.triples((None, RDF.type, None)))) == 4
    assert len(list(G.triples((URIRef("http://test/bar"), None, None)))) == 2
    assert len(list(G.triples((None, URIRef("http://test/d"), None)))) == 3

    # Test __len__
    assert len(G) == 8

    # assert context iteration
    for g in G.contexts():
        assert isinstance(g, Graph)

    # Test __contains__
    assert (URIRef("http://test/foo"), RDF.type, RDFS.Resource) in G

    barPredicates = [URIRef("http://test/d"), RDFS.isDefinedBy]
    assert (
        len(list(G.triples_choices((URIRef("http://test/bar"), barPredicates, None))))
        == 2
    )


def test_aggregate2():
    memStore = plugin.get("Memory", Store)()
    graph1 = Graph(memStore, URIRef("http://example.com/graph1"))
    graph2 = Graph(memStore, URIRef("http://example.com/graph2"))
    graph3 = Graph(memStore, URIRef("http://example.com/graph3"))

    for n3Str, graph in [
        (testGraph1N3, graph1),
        (testGraph2N3, graph2),
        (testGraph3N3, graph3),
    ]:
        graph.parse(StringIO(n3Str), format="n3")

    graph4 = Graph(memStore, RDFS)
    graph4.parse(data=testGraph1N3, format="n3")
    g = ConjunctiveGraph(memStore)
    assert g is not None
    assert len(list(g.quads((None, None, None, None)))) == 11
    assert len(list(g.contexts())) == 4
    logger.debug(list(g.contexts()))
    assert (
        len(list(g.quads((None, None, None, URIRef("http://example.com/graph2"))))) == 4
    )
    assert (
        len(
            list(
                g.quads(
                    (None, None, None, URIRef("http://www.w3.org/2000/01/rdf-schema#"))
                )
            )
        )
        == 6
    )
