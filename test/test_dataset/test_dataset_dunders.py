import os
from test.data import *

import pytest

from rdflib.graph import DATASET_DEFAULT_GRAPH_ID, Dataset, Graph
from rdflib.namespace import DC, DCTERMS, FOAF, RDF, RDFS, SKOS, XSD, Namespace
from rdflib.term import BNode, Literal, URIRef

example2_root = os.path.join(
    CONSISTENT_DATA_DIR, "example-2-default-and-two-named-graphs."
)
example3_root = os.path.join(CONSISTENT_DATA_DIR, "example-3-three-named-graphs.")
example4_root = os.path.join(
    CONSISTENT_DATA_DIR, "example-4-default-plus-two-named-graphs-and-one-bnode."
)


@pytest.fixture
def example2(request):
    d = Dataset()
    d.bind("ex", Namespace("http://example.org/"))

    # alice = BNode(_sn_gen=bnode_sn_generator)  # Alice
    # bob = BNode(_sn_gen=bnode_sn_generator)  # Bob

    # logger.debug(f"Alice: {alice.n3()}, Bob {bob.n3()}")

    alice = BNode()  # Alice
    bob = BNode()  # Bob

    alice_graph = d.graph(alice_uri)
    bob_graph = d.graph(bob_uri)

    d.add((alice_uri, DCTERMS.publisher, Literal("Alice")))
    d.add((bob_uri, DCTERMS.publisher, Literal("Bob")))

    alice_graph.add((alice, FOAF.mbox, URIRef("mailto:alice@work.example.org")))
    alice_graph.add((alice, FOAF.name, Literal("Alice")))

    bob_graph.add((bob, FOAF.name, Literal("Bob")))
    bob_graph.add((bob, FOAF.mbox, URIRef("mailto:bob@oldcorp.example.org")))
    bob_graph.add((bob, FOAF.knows, alice))

    yield d, alice_graph, bob_graph


def test_dataset_dunders(example2):
    d0, a, b = example2  # d0 = default_graph + a + b

    d1 = Dataset()
    d1 += a  # default_graph = a

    d2 = Dataset()
    d2 += a  # d1 == d2

    d3 = Dataset()
    d3 += b  # default_graph = b

    assert d0 == d1
    assert d0 > d1

    assert d1 > d2
    assert d2 > d1
    assert d0 > d3
    assert d1 > d3

    assert d0 == d1
    assert d1 == d2
    assert d1 == d3
