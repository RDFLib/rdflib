from rdflib.graph import Dataset, Graph
from rdflib.term import URIRef

dataset = Dataset(default_union=True)
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


# Test implicit inclusive dataset
# The query's default graph should contain a merge of all graphs:
# The service's default graph + all the service's named graphs
def test_inclusive():
    query = """
        SELECT ?s ?p ?o
        WHERE {?s ?p ?o}
        ORDER BY ?s
    """
    results = list(dataset.query(query))
    assert results == [
        (URIRef("urn:s0"), URIRef("urn:p0"), URIRef("urn:o0")),
        (URIRef("urn:s1"), URIRef("urn:p1"), URIRef("urn:o1")),
        (URIRef("urn:s2"), URIRef("urn:p2"), URIRef("urn:o2")),
        (URIRef("urn:s3"), URIRef("urn:p3"), URIRef("urn:o3")),
    ]


# Test explicit default graph with inclusive dataset
def test_default_from_1():
    query = """
        SELECT ?s ?p ?o
        FROM <urn:g1>
        WHERE {?s ?p ?o}
    """
    results = list(dataset.query(query))
    assert results == [(URIRef("urn:s1"), URIRef("urn:p1"), URIRef("urn:o1"))]


# test that we include more than one graph into the default graph
def test_default_from_2():
    query = """
        SELECT ?s ?p ?o
        FROM <urn:g1>
        FROM <urn:g2>
        WHERE {?s ?p ?o}
        ORDER BY ?s
    """
    results = list(dataset.query(query))
    assert results == [
        (URIRef("urn:s1"), URIRef("urn:p1"), URIRef("urn:o1")),
        (URIRef("urn:s2"), URIRef("urn:p2"), URIRef("urn:o2")),
    ]


# Since there is a FROM clause, we consider RDF dataset explicit
# Thus if FROM NAMED is not defined, named graph is considered empty set
def test_named_from():
    query = """
        SELECT ?s ?p ?o
        FROM <urn:g1>
        WHERE {
            graph ?g {?s ?p ?o}
        } ORDER BY ?s
    """
    results = list(dataset.query(query))
    assert results == [], "no result expected"


# Test explicit named graphs with inclusive dataset
def test_named_from_named_1():
    query = """
        SELECT ?g ?s ?p ?o
        FROM NAMED <urn:g1>
        WHERE {
            graph ?g {?s ?p ?o}
        }
    """
    results = list(dataset.query(query))
    assert results == [
        (URIRef("urn:g1"), URIRef("urn:s1"), URIRef("urn:p1"), URIRef("urn:o1"))
    ]


# test that we include more than one graph into the named graphs
def test_named_from_named_2():
    query = """
    SELECT ?g ?s ?p ?o
    FROM NAMED <urn:g1>
    FROM NAMED <urn:g2>
    WHERE {
        graph ?g {?s ?p ?o}
    } ORDER BY ?g
    """
    results = list(dataset.query(query))
    assert results == [
        (URIRef("urn:g1"), URIRef("urn:s1"), URIRef("urn:p1"), URIRef("urn:o1")),
        (URIRef("urn:g2"), URIRef("urn:s2"), URIRef("urn:p2"), URIRef("urn:o2")),
    ]


# Since there is a FROM NAMED clause, we consider RDF dataset explicit
# Thus if FROM is not defined, default graph is considered empty
def test_default_from_named():
    results = list(
        dataset.query("SELECT ?g ?s ?p ?o FROM NAMED <urn:g1> WHERE {?s ?p ?o}")
    )
    assert results == [], "no result expected"


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
