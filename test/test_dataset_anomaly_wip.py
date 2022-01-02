import os
from pprint import pformat
import warnings
import pytest
from rdflib import (
    logger,
    BNode,
    Graph,
    ConjunctiveGraph,
    Dataset,
    Literal,
    Namespace,
    OWL,
    URIRef,
)

from rdflib.graph import DATASET_DEFAULT_GRAPH_ID

# from rdflib.store import Store

# timblcardn3 = open(
#     os.path.join(os.path.dirname(__file__), "consistent_test_data", "timbl-card.n3")
# ).read()


# sportquadsnq = open(
#     os.path.join(os.path.dirname(__file__), "consistent_test_data", "sportquads.nq")
# ).read()


# example1_trig = open(
#     os.path.join(os.path.dirname(__file__), "consistent_test_data", "example-1.trig")
# ).read()


list_of_nquads = [
    (
        URIRef("http://example.com/resource/student_10"),
        URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
        URIRef("http://example.com/ontology/Student"),
        URIRef("http://example.org/graph/students"),
    ),
    (
        URIRef("http://example.com/resource/student_10"),
        URIRef("http://xmlns.com/foaf/0.1/name"),
        Literal("Venus Williams"),
        URIRef("http://example.org/graph/students"),
    ),
    (
        URIRef("http://example.com/resource/student_20"),
        URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
        URIRef("http://example.com/ontology/Student"),
        URIRef("http://example.org/graph/students"),
    ),
    (
        URIRef("http://example.com/resource/student_20"),
        URIRef("http://xmlns.com/foaf/0.1/name"),
        Literal("Demi Moore"),
        URIRef("http://example.org/graph/students"),
    ),
    (
        URIRef("http://example.com/resource/sport_100"),
        URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
        URIRef("http://example.com/ontology/Sport"),
        URIRef("http://example.org/graph/sports"),
    ),
    (
        URIRef("http://example.com/resource/sport_100"),
        URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
        Literal("Tennis"),
        URIRef("http://example.org/graph/sports"),
    ),
    (
        URIRef("http://example.com/resource/student_10"),
        URIRef("http://example.com/ontology/practises"),
        URIRef("http://example.com/resource/sport_100"),
        URIRef("http://example.org/graph/practise"),
    ),
]

michel = URIRef("urn:michel")
tarek = URIRef("urn:tarek")
bob = URIRef("urn:bob")
likes = URIRef("urn:likes")
hates = URIRef("urn:hates")
pizza = URIRef("urn:pizza")
cheese = URIRef("urn:cheese")

c1 = URIRef("urn:context-1")
c2 = URIRef("urn:context-2")


# operator.ior(a, b)
# operator.__ior__(a, b)

#     a = ior(a, b) is equivalent to a |= b.


def test_dataset_equal_to_dataset_default():
    d = Dataset()
    assert d == d.graph(DATASET_DEFAULT_GRAPH_ID)


def test_issue319_add_graph_as_dataset_DEFAULT_via_sparqlupdate():
    ds = Dataset()
    ds.update("INSERT DATA { <urn:tarek> <urn:hates> <urn:cheese> . }")

    ncontexts = len(list(ds.contexts()))

    assert ncontexts == 1


def test_issue319_add_graph_as_dataset_NAMED_DEFAULT_via_sparqlupdate():
    ds = Dataset()
    ds.update("INSERT DATA { <urn:tarek> <urn:hates> <urn:cheese> . }")
    ds.update(
        "INSERT DATA { GRAPH <urn:x-rdflib-default> { <urn:tarek> <urn:hates> <urn:pizza> . } }"
    )

    ncontexts = len(list(ds.contexts()))

    assert ncontexts == 1


def test_issue319_add_graph_as_dataset_CONTEXT_via_sparqlupdate():
    ds = Dataset()
    ds.update("INSERT DATA { <urn:tarek> <urn:hates> <urn:cheese> . }")
    ds.update(
        "INSERT DATA { GRAPH <urn:context1> { <urn:tarek> <urn:hates> <urn:pizza> . } }"
    )

    ncontexts = len(list(ds.contexts()))

    assert ncontexts == 2


def test_issue319_parse_graph_as_dataset_DEFAULT_turtle():
    ds = Dataset()
    ds.update("INSERT DATA { <urn:tarek> <urn:hates> <urn:cheese> . }")
    ds.parse(data="<urn:tarek> <urn:likes> <urn:pizza> .", format="ttl")

    ncontexts = len(list(ds.contexts()))

    assert ncontexts == 1


def test_issue319_parse_graph_as_dataset_CONTEXT_nquads():
    ds = Dataset()
    ds.update("INSERT DATA { <urn:tarek> <urn:hates> <urn:cheese> . }")
    ds.parse(
        data="<urn:tarek> <urn:likes> <urn:pizza> <urn:context-0> .", format="nquads"
    )

    ncontexts = len(list(ds.contexts()))

    assert ncontexts == 2


def test_issue319_parse_graph_as_dataset_CONTEXT_trig():
    ds = Dataset()
    ds.update("INSERT DATA { <urn:tarek> <urn:hates> <urn:cheese> . }")
    ds.parse(
        data="@prefix ex: <http://example.org/graph/> . @prefix ont: <http://example.com/ontology/> . ex:practise { <http://example.com/resource/student_10> ont:practises <http://example.com/resource/sport_100> . }",
        format="trig",
    )

    ncontexts = len(list(ds.contexts()))

    assert ncontexts == 2


def test_issue319_parse_graph_with_publicid_as_dataset_CONTEXT():
    ds = Dataset()
    ds.update("INSERT DATA { <urn:tarek> <urn:hates> <urn:cheese> . }")
    ds.parse(
        data="<urn:tarek> <urn:likes> <urn:pizza> .",
        publicID="urn:context-a",
        format="ttl",
    )
    ncontexts = len(list(ds.contexts()))

    assert ncontexts == 2


def test_issue319_parse_bnode_graph_as_dataset_DEFAULT():
    ds = Dataset()
    ds.update("INSERT DATA { <urn:tarek> <urn:hates> <urn:cheese> . }")
    data = """_:a <urn:likes> <urn:pizza> ."""
    ds.parse(data=data, format="ttl")

    ncontexts = len(list(ds.contexts()))

    assert ncontexts == 1


def test_issue319_parse_graph_with_bnode_identifier_as_dataset_CONTEXT():
    ds = Dataset()
    ds.update("INSERT DATA { <urn:tarek> <urn:hates> <urn:cheese> . }")

    ds.parse(data="<urn:tarek> <urn:likes> <urn:pizza> .", format="ttl")

    g = Graph(identifier=BNode())
    g.parse(data="<a> <b> <c> .", format="ttl")

    assert ds.add_graph(g) is not None

    ncontexts = len(list(ds.contexts()))

    assert ncontexts == 2


def test_issue319_parse_conjunctivegraph_with_bnode_identifier_as_dataset_CONTEXT():
    ds = Dataset()
    ds.update("INSERT DATA { <urn:tarek> <urn:hates> <urn:cheese> . }")

    ds.parse(data="<urn:tarek> <urn:likes> <urn:pizza> .", format="ttl")

    g = ConjunctiveGraph(identifier=BNode())
    g.parse(data="<a> <b> <c> .", format="ttl")
    g.addN([(tarek, likes, michel, "urn:context-0")])

    # FIXME: add to dataset operators test
    # assert ds.add_graph(g, preserve_contexts=True) is not None
    assert ds.add_graph(g) is not None

    ncontexts = len(list(ds.contexts()))

    assert ncontexts == 2


def test_issue319_parse_graph_as_dataset_DEFAULT():
    ds = Dataset()
    ds.update("INSERT DATA { <urn:tarek> <urn:hates> <urn:cheese> . }")

    ds.parse(data="<urn:tarek> <urn:likes> <urn:pizza> .", format="ttl")

    ncontexts = len(list(ds.contexts()))

    assert ncontexts == 1
