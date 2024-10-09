from pathlib import Path

from rdflib import URIRef
from test.utils.graph import cached_graph

TEST_DIR = Path(__file__).parent
TEST_DATA_DIR = TEST_DIR / "data"

ALICE_URI = URIRef("http://example.org/alice")
BOB_URI = URIRef("http://example.org/bob")

MICHEL = URIRef("urn:example:michel")
TAREK = URIRef("urn:example:tarek")
BOB = URIRef("urn:example:bob")
LIKES = URIRef("urn:example:likes")
HATES = URIRef("urn:example:hates")
PIZZA = URIRef("urn:example:pizza")
CHEESE = URIRef("urn:example:cheese")
CONTEXT0 = URIRef("urn:example:context-0")
CONTEXT1 = URIRef("urn:example:context-1")
CONTEXT2 = URIRef("urn:example:context-2")


SIMPLE_TRIPLE_GRAPH = cached_graph((TEST_DATA_DIR / "variants" / "simple_triple.py",))

__all__ = [
    "TEST_DIR",
    "TEST_DATA_DIR",
    "SIMPLE_TRIPLE_GRAPH",
    "ALICE_URI",
    "BOB_URI",
    "MICHEL",
    "TAREK",
    "BOB",
    "LIKES",
    "HATES",
    "PIZZA",
    "CHEESE",
    "CONTEXT0",
    "CONTEXT1",
    "CONTEXT2",
]
