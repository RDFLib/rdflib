"""This runs the turtle tests for the W3C RDF Working Group's N-Quads
test suite."""

import os
from pathlib import Path
from test.data import TEST_DATA_DIR
from test.utils import file_uri_to_path
from test.utils.manifest import RDFT, RDFTest, read_manifest
from typing import Callable, Dict, Set

import pytest

from rdflib import Graph
from rdflib.compare import graph_diff, isomorphic
from rdflib.namespace import Namespace, split_uri
from rdflib.term import Node, URIRef

verbose = False


def turtle(test: RDFTest):
    g = Graph()

    try:
        # base = "http://www.w3.org/2013/TurtleTests/" + split_uri(test.action)[1]
        base = "https://w3c.github.io/N3/tests/TurtleTests/" + split_uri(test.action)[1]

        g.parse(test.action, publicID=base, format="turtle")
        if not test.syntax:
            raise AssertionError("Input shouldn't have parsed!")

        if test.result:  # eval test
            res = Graph()
            assert not isinstance(test.result, tuple)
            res.parse(test.result, format="nt")

            if verbose:
                both, first, second = graph_diff(g, res)
                if not first and not second:
                    return
                print("Diff:")
                # print "%d triples in both"%len(both)
                print("Turtle Only:")
                for t in first:
                    print(t)

                print("--------------------")
                print("NT Only")
                for t in second:
                    print(t)
                raise Exception("Graphs do not match!")

            assert isomorphic(
                g, res
            ), "graphs must be the same, expected\n%s\n, got\n%s" % (
                g.serialize(),
                res.serialize(),
            )

    except:
        if test.syntax:
            raise


testers: Dict[Node, Callable[[RDFTest], None]] = {
    RDFT.TestTurtlePositiveSyntax: turtle,
    RDFT.TestTurtleNegativeSyntax: turtle,
    RDFT.TestTurtleEval: turtle,
    RDFT.TestTurtleNegativeEval: turtle,
}

NAMESPACE = Namespace("https://w3c.github.io/N3/tests/TurtleTests/manifest.ttl#")
EXPECTED_FAILURES: Dict[str, str] = {}

if os.name == "nt":
    for test in ["literal_with_LINE_FEED", "turtle-subm-15", "turtle-subm-16"]:
        EXPECTED_FAILURES[test] = "Issue with nt parser and line endings on windows"


@pytest.mark.parametrize(
    "rdf_test_uri, type, rdf_test",
    read_manifest(
        os.path.join(TEST_DATA_DIR, "suites/w3c/n3/TurtleTests/manifest.ttl")
    ),
)
def test_manifest(rdf_test_uri: URIRef, type: Node, rdf_test: RDFTest):
    suffix = rdf_test_uri.split("#")[1]
    if suffix in EXPECTED_FAILURES:
        pytest.xfail(EXPECTED_FAILURES[suffix])
    testers[type](rdf_test)
