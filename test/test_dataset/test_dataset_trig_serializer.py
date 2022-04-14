import os
from test.data import *

from rdflib import Dataset, logger
from rdflib.namespace import DCTERMS, FOAF, Namespace
from rdflib.term import BNode, Literal, URIRef

example2_root = os.path.join(
    CONSISTENT_DATA_DIR, "example-2-default-and-two-named-graphs."
)
example3_root = os.path.join(CONSISTENT_DATA_DIR, "example-3-three-named-graphs.")
example4_root = os.path.join(
    CONSISTENT_DATA_DIR, "example-4-default-plus-two-named-graphs-and-one-bnode."
)


def test_dataset_trig_serializer():
    d = Dataset()
    d.bind("ex", Namespace("http://example.org/"))
    d.bind("genid", Namespace("http://rdlib.net/.well-known/genid/rdflib/"))

    alice = BNode()  # Alice
    bob = BNode()  # Bob

    harry_uri = BNode()  # Harry
    harry = BNode()  # Harry

    tom_uri = BNode()  # Tom
    tom = BNode()  # Tom

    alice_graph = d.graph(alice_uri)
    bob_graph = d.graph(bob_uri)
    harry_graph = d.graph(harry_uri)
    tom_graph = d.graph(tom_uri)

    d.add((alice_uri, DCTERMS.publisher, Literal("Alice")))
    d.add((bob_uri, DCTERMS.publisher, Literal("Bob")))
    d.add((harry_uri, DCTERMS.publisher, Literal("Harry")))
    d.add((tom_uri, DCTERMS.publisher, Literal("Tom")))

    alice_graph.add((alice, FOAF.mbox, URIRef("mailto:alice@work.example.org")))
    alice_graph.add((alice, FOAF.name, Literal("Alice")))

    bob_graph.add((bob, FOAF.name, Literal("Bob")))
    bob_graph.add((bob, FOAF.mbox, URIRef("mailto:bob@oldcorp.example.org")))
    bob_graph.add((bob, FOAF.knows, alice))
    bob_graph.add((bob, FOAF.knows, harry))

    tom_graph.add((tom, FOAF.name, Literal("Tom")))
    tom_graph.add((tom, FOAF.mbox, URIRef("mailto:tom@work.example.org")))

    harry_graph.add((harry, FOAF.name, Literal("Harry")))
    harry_graph.add((harry, FOAF.mbox, URIRef("mailto:harry@work.example.org")))

    d1 = Dataset()
    d1.bind("ex", Namespace("http://example.org/"))

    trigdata1 = d.serialize(format="trig")

    d1.parse(data=trigdata1, format="trig")

    trigdata2 = d1.serialize(format="trig")

    d2 = Dataset()
    d2.bind("ex", Namespace("http://example.org/"))

    nquadsdata = d1.serialize(format="nquads")
    d2.parse(data=nquadsdata, format="nquads")

    assert len(list(d.quads((None, None, None, None)))) != 0

    assert len(list(d.quads((None, None, None, None)))) == len(
        list(d1.quads((None, None, None, None)))
    )

    assert len(list(d1.quads((None, None, None, None)))) == len(
        list(d2.quads((None, None, None, None)))
    )

    # logger.debug(f"\nD0:{os.linesep.join(sorted(d.serialize(format='nquads').split(os.linesep)))}")
    # logger.debug(f"\nD1:{os.linesep.join(sorted(d1.serialize(format='nquads').split(os.linesep)))}")
    # logger.debug(f"\nD2:{os.linesep.join(sorted(d2.serialize(format='nquads').split(os.linesep)))}")
