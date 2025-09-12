from io import StringIO

from rdflib import Dataset, Graph, logger, plugin
from rdflib.graph import ReadOnlyGraphAggregate
from rdflib.namespace import RDF, RDFS
from rdflib.store import Store
from rdflib.term import URIRef

TEST_GRAPH_1N3 = """
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <http://test/> .
:foo a rdfs:Class.
:bar :d :c.
:a :d :c.
"""


TEST_GRAPH_2N3 = """
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <http://test/> .
@prefix log: <http://www.w3.org/2000/10/swap/log#>.
:foo a rdfs:Resource.
:bar rdfs:isDefinedBy [ a log:Formula ].
:a :d :e.
"""

TEST_GRAPH_3N3 = """
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix log: <http://www.w3.org/2000/10/swap/log#>.
@prefix : <http://test/> .
<> a log:N3Document.
"""

SPARQL_Q = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT *
FROM NAMED <http://example.com/graph1>
FROM NAMED <http://example.com/graph2>
FROM NAMED <http://example.com/graph3>
FROM <http://www.w3.org/2000/01/rdf-schema#>

WHERE {?sub ?pred rdfs:Class }"""

SPARQL_Q2 = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?class
WHERE { GRAPH ?graph { ?member a ?class } }"""

SPARQL_Q3 = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX log: <http://www.w3.org/2000/10/swap/log#>
SELECT ?n3Doc
WHERE {?n3Doc a log:N3Document }"""


def test_aggregate_raw():
    mem_store = plugin.get("Memory", Store)()
    graph1 = Graph(mem_store)
    graph2 = Graph(mem_store)
    graph3 = Graph(mem_store)

    for n3_str, graph in [
        (TEST_GRAPH_1N3, graph1),
        (TEST_GRAPH_2N3, graph2),
        (TEST_GRAPH_3N3, graph3),
    ]:
        graph.parse(StringIO(n3_str), format="n3")

    g = ReadOnlyGraphAggregate([graph1, graph2, graph3])

    # Test triples
    assert len(list(g.triples((None, RDF.type, None)))) == 4
    assert len(list(g.triples((URIRef("http://test/bar"), None, None)))) == 2
    assert len(list(g.triples((None, URIRef("http://test/d"), None)))) == 3

    # Test __len__
    assert len(g) == 8

    # assert context iteration
    for g in g.contexts():
        assert isinstance(g, Graph)

    # Test __contains__
    assert (URIRef("http://test/foo"), RDF.type, RDFS.Resource) in g

    bar_predicates = [URIRef("http://test/d"), RDFS.isDefinedBy]
    assert (
        len(list(g.triples_choices((URIRef("http://test/bar"), bar_predicates, None))))
        == 2
    )


def test_aggregate2():
    mem_store = plugin.get("Memory", Store)()
    graph1 = Graph(mem_store, URIRef("http://example.com/graph1"))
    graph2 = Graph(mem_store, URIRef("http://example.com/graph2"))
    graph3 = Graph(mem_store, URIRef("http://example.com/graph3"))

    for n3_str, graph in [
        (TEST_GRAPH_1N3, graph1),
        (TEST_GRAPH_2N3, graph2),
        (TEST_GRAPH_3N3, graph3),
    ]:
        graph.parse(StringIO(n3_str), format="n3")

    graph4 = Graph(mem_store, RDFS)
    graph4.parse(data=TEST_GRAPH_1N3, format="n3")
    g = Dataset(store=mem_store, default_union=True)
    assert g is not None
    assert len(list(g.quads((None, None, None, None)))) == 11
    assert len(list(g.contexts())) == 5
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
