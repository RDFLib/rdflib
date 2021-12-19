"""This runs the nquads tests for the W3C RDF Working Group's N-Quads
test suite."""

from typing import Callable, Dict
from rdflib import ConjunctiveGraph
from rdflib.term import Node, URIRef
from test.manifest import RDFT, RDFTest, read_manifest
import pytest

verbose = False


def nquads(test):
    g = ConjunctiveGraph()

    try:
        g.parse(test.action, format="nquads")
        if not test.syntax:
            raise AssertionError("Input shouldn't have parsed!")
    except:
        if test.syntax:
            raise


testers: Dict[Node, Callable[[RDFTest], None]] = {
    RDFT.TestNQuadsPositiveSyntax: nquads,
    RDFT.TestNQuadsNegativeSyntax: nquads,
}


@pytest.mark.parametrize(
    "rdf_test_uri, type, rdf_test",
    read_manifest("test/w3c/nquads/manifest.ttl"),
)
def test_manifest(rdf_test_uri: URIRef, type: Node, rdf_test: RDFTest):
    testers[type](rdf_test)
