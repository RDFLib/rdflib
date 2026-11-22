from rdflib.graph import Dataset, Graph
from rdflib.term import URIRef

dataset = Dataset(default_union=False)
# Adding into default graph
dataset.add((URIRef("urn:s0"), URIRef("urn:p0"), URIRef("urn:o0")))
# Adding into named graphs
dataset.add(
    (
        URIRef("urn:s1"),
        URIRef("urn:p1"),
        URIRef("urn:o1"),
        Graph(identifier=URIRef("urn:g1")),
    )
)

dataset.add(
    (
        URIRef("urn:s2"),
        URIRef("urn:p2"),
        URIRef("urn:o2"),
        Graph(identifier=URIRef("urn:g2")),
    )
)

dataset.add(
    (
        URIRef("urn:s3"),
        URIRef("urn:p3"),
        URIRef("urn:o3"),
        Graph(identifier=URIRef("urn:g3")),
    )
)


# Test implicit exlusive dataset
def test_exclusive():
    results = list(dataset.query("SELECT ?s ?p ?o WHERE {?s ?p ?o}"))
    assert results == [(URIRef("urn:s0"), URIRef("urn:p0"), URIRef("urn:o0"))]


# Test explicit default graph with exclusive dataset
def test_from():
    query = """
        SELECT ?s ?p ?o
        FROM <urn:g1>
        WHERE {?s ?p ?o}
    """
    results = list(dataset.query(query))
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
    results = list(dataset.query(query))
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
    results = list(dataset.query(query))
    assert results == [
        (None, URIRef("urn:s1"), URIRef("urn:p1"), URIRef("urn:o1")),
        (URIRef("urn:g2"), URIRef("urn:s2"), URIRef("urn:p2"), URIRef("urn:o2")),
    ]


def test_ask_from():
    query = """
        ASK
        FROM <urn:g1>
        WHERE {?s ?p ?o}
    """
    results = bool(dataset.query(query))
    assert results
