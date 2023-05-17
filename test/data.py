from pathlib import Path

from rdflib import URIRef
from rdflib.graph import Graph

TEST_DIR = Path(__file__).parent
TEST_DATA_DIR = TEST_DIR / "data"

alice_uri = URIRef("http://example.org/alice")
bob_uri = URIRef("http://example.org/bob")

michel = URIRef("urn:example:michel")
tarek = URIRef("urn:example:tarek")
bob = URIRef("urn:example:bob")
likes = URIRef("urn:example:likes")
hates = URIRef("urn:example:hates")
pizza = URIRef("urn:example:pizza")
cheese = URIRef("urn:example:cheese")

context0 = URIRef("urn:example:context-0")
context1 = URIRef("urn:example:context-1")
context2 = URIRef("urn:example:context-2")


simple_triple_graph = Graph().add(
    (
        URIRef("http://example.org/subject"),
        URIRef("http://example.org/predicate"),
        URIRef("http://example.org/object"),
    )
)
"""
A simple graph with a single triple. This is equivalent to the following RDF files:

* ``test/data/variants/simple_triple.nq``
* ``test/data/variants/simple_triple.nt``
* ``test/data/variants/simple_triple.ttl``
* ``test/data/variants/simple_triple.xml``
"""
