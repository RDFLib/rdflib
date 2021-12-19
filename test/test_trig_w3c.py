"""Runs the tests for the W3C RDF Working Group's TriG test suite.

"""

from typing import Callable, Dict
from rdflib import ConjunctiveGraph
from rdflib.namespace import Namespace, split_uri
from rdflib.compare import graph_diff, isomorphic
from rdflib.term import Node, URIRef

from test.manifest import RDFT, RDFTest, read_manifest
import pytest

import os

verbose = False


def trig(test):
    g = ConjunctiveGraph()

    try:
        base = "http://www.w3.org/2013/TriGTests/" + split_uri(test.action)[1]

        g.parse(test.action, publicID=base, format="trig")
        if not test.syntax:
            raise AssertionError("Input shouldn't have parsed!")

        if test.result:  # eval test
            res = ConjunctiveGraph()
            res.parse(test.result, format="nquads")

            if verbose:

                both, first, second = graph_diff(g, res)
                if not first and not second:
                    return

                print("===============================")
                print("TriG")
                print(g.serialize(format="nquads"))
                print("===============================")
                print("NQuads")
                print(res.serialize(format="nquads"))
                print("===============================")

                print("Diff:")
                # print "%d triples in both"%len(both)
                print("TriG Only:")
                for t in first:
                    print(t)

                print("--------------------")
                print("NQuads Only")
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
    RDFT.TestTrigPositiveSyntax: trig,
    RDFT.TestTrigNegativeSyntax: trig,
    RDFT.TestTrigEval: trig,
    RDFT.TestTrigNegativeEval: trig,
}

NAMESPACE = Namespace(
    "https://dvcs.w3.org/hg/rdf/raw-file/default/trig/tests/manifest.ttl#"
)
EXPECTED_FAILURES: Dict[URIRef, str] = {}

if os.name == "nt":
    for test in ["literal_with_LINE_FEED", "trig-subm-15", "trig-subm-16"]:
        EXPECTED_FAILURES[
            NAMESPACE[test]
        ] = "Issue with nt parser and line endings on windows"


@pytest.mark.parametrize(
    "rdf_test_uri, type, rdf_test",
    read_manifest("test/w3c/trig/manifest.ttl"),
)
def test_manifest(rdf_test_uri: URIRef, type: Node, rdf_test: RDFTest):
    if rdf_test_uri in EXPECTED_FAILURES:
        pytest.xfail(EXPECTED_FAILURES[rdf_test_uri])
    testers[type](rdf_test)
