"""This runs the nt tests for the W3C RDF Working Group's N-Quads
test suite."""
import os
from typing import Callable, Dict

from rdflib import Graph
from rdflib.term import Node, URIRef
from test import TEST_DIR
from test.manifest import RDFT, RDFTest, read_manifest

import pytest

verbose = False


def nt(test):
    g = Graph()

    try:
        g.parse(test.action, format="nt")
        if not test.syntax:
            raise AssertionError("Input shouldn't have parsed!")
    except:
        if test.syntax:
            raise


testers: Dict[Node, Callable[[RDFTest], None]] = {
    RDFT.TestNTriplesPositiveSyntax: nt,
    RDFT.TestNTriplesNegativeSyntax: nt,
}


@pytest.mark.parametrize(
    "rdf_test_uri, type, rdf_test",
    read_manifest(os.path.join(TEST_DIR, "w3c/nt/manifest.ttl"), legacy=True),
)
def test_manifest(rdf_test_uri: URIRef, type: Node, rdf_test: RDFTest):
    testers[type](rdf_test)
