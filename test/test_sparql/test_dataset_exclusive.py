from test.utils.sparql_checker import ctx_configure_rdflib
from typing import Generator

import pytest

from rdflib.graph import ConjunctiveGraph
from rdflib.term import URIRef

graph = ConjunctiveGraph()
# Adding into default graph
graph.add((URIRef("urn:s0"), URIRef("urn:p0"), URIRef("urn:o0")))
# Adding into named graphs
graph.add((URIRef("urn:s1"), URIRef("urn:p1"), URIRef("urn:o1"), URIRef("urn:g1")))

graph.add((URIRef("urn:s2"), URIRef("urn:p2"), URIRef("urn:o2"), URIRef("urn:g2")))

graph.add((URIRef("urn:s3"), URIRef("urn:p3"), URIRef("urn:o3"), URIRef("urn:g3")))


# Set SPARQL_DEFAULT_GRAPH_UNION to false to make dataset inclusive
# Set it back at the end of the test
@pytest.fixture(scope="module", autouse=True)
def configure_rdflib() -> Generator[None, None, None]:
    with ctx_configure_rdflib():
        yield None


# Test implicit exlusive dataset
def test_exclusive():
    results = list(graph.query("SELECT ?s ?p ?o WHERE {?s ?p ?o}"))
    assert results == [(URIRef("urn:s0"), URIRef("urn:p0"), URIRef("urn:o0"))]


# Test explicit default graph with exclusive dataset
def test_from():
    query = """
        SELECT ?s ?p ?o
        FROM <urn:g1>
        WHERE {?s ?p ?o}
    """
    results = list(graph.query(query))
    assert results == [(URIRef("urn:s1"), URIRef("urn:p1"), URIRef("urn:o1"))]


# Test explicit named graphs with exclusive dataset
def test_from_named():
    query = """
        SELECT
        ?g ?s ?p ?o
        FROM NAMED <urn:g1>
        WHERE {
            graph ?g {?s ?p ?o}
        }
    """
    results = list(graph.query(query))
    assert results == [
        (URIRef("urn:g1"), URIRef("urn:s1"), URIRef("urn:p1"), URIRef("urn:o1"))
    ]


# Test that we can use from and from named in the same query
def test_from_and_from_named():
    query = """
        SELECT ?g ?s ?p ?o
        FROM <urn:g1>
        FROM NAMED <urn:g2>
        WHERE {
            {?s ?p ?o}
            UNION {graph ?g {?s ?p ?o}}
        } ORDER BY ?s
    """
    results = list(graph.query(query))
    assert results == [
        (None, URIRef("urn:s1"), URIRef("urn:p1"), URIRef("urn:o1")),
        (URIRef("urn:g2"), URIRef("urn:s2"), URIRef("urn:p2"), URIRef("urn:o2")),
    ]
