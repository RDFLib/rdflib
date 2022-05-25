"""This runs the TriX tests for RDFLib's informally-assembled TriX
test suite."""
from test.data import TEST_DATA_DIR
from test.utils.manifest import RDFTest, read_manifest
from test.utils.namespace import RDFT
from typing import Callable, Dict

import pytest

from rdflib import ConjunctiveGraph, logger
from rdflib.compare import graph_diff, isomorphic
from rdflib.namespace import split_uri
from rdflib.term import Node, URIRef

verbose = False


def trix(test: RDFTest):
    g = ConjunctiveGraph()

    try:

        base = "https://rdflib.github.io/tests/trix/" + split_uri(test.action)[1]

        g.parse(test.action, publicID=base, format="trix")

        if not test.syntax:
            raise AssertionError("Input shouldn't have parsed!")

        if test.result:  # eval test
            logger.debug(f"TEST RESULT {test.result}")
            res = ConjunctiveGraph()
            assert not isinstance(test.result, tuple)
            res.parse(test.result, publicID=base)

            if verbose:
                both, first, second = graph_diff(g, res)
                if not first and not second:
                    return
                print("Diff:")

                print("TriX Only:")
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
                g.serialize(format="nquads"),
                res.serialize(format="nquads"),
            )

    except Exception:
        if test.syntax:
            raise


testers: Dict[Node, Callable[[RDFTest], None]] = {
    RDFT.TestTrixPositiveSyntax: trix,
    RDFT.TestTrixNegativeSyntax: trix,
    RDFT.TestTrixEval: trix,
}


# TriX star parsing/serialization not yet implemented for RDFLib
star_skipped = [
    "trix-jena-star-1",
    "trix-jena-star-2",
    "trix-jena-star-bad-asserted-1",
    "trix-jena-star-bad-asserted-2",
    "trix-jena-star-bad-emb-1",
    "trix-jena-star-bad-emb-2",
    "trix-jena-star-bad-emb-nested-1",
    "trix-jena-star-bad-emb-nested-2",
    "trix-jena-star-bad-emb-nested-3",
]

eval_skipped = [
    "trix-jena-04",  # Missing namespace
    "trix-jena-12",  # tags in Literal value
    "trix-jena-13",  # tags in Literal value
    "trix-jena-14",  # tags in Literal value
    "trix-jena-ns-1",  # Multiple namespaces
    "trix-jena-ns-2",  # Multiple namespaces
    "trix-jena-w3c-2",  # Missing namespace
    "trix-ng4j-relativeuris",  # Can't create test file of expected
]


positive_syntax_skipped = [
    "trix-jena-ex-2",  # Multiple namespaces
    "trix-jena-ex-3",  # tags in Literal value
    "trix-jena-ex-4",  # tags in Literal value
    "trix-ng4j-extended",  # xslt processing required
    "trix-ng4j-missingnamespace",  # Missing namespace
]


EXPECTED_FAILURES: Dict[str, str] = {}

for test in star_skipped:
    EXPECTED_FAILURES[test] = "TriX Star NYI"


for test in positive_syntax_skipped:
    EXPECTED_FAILURES[test] = "Known issue with TriX parser"

for test in eval_skipped:
    EXPECTED_FAILURES[test] = "Known issue with TriX eval"


@pytest.mark.parametrize(
    "rdf_test_uri, type, rdf_test",
    read_manifest(TEST_DATA_DIR / "suites" / "trix" / "manifest.ttl"),
)
def test_manifest(rdf_test_uri: URIRef, type: Node, rdf_test: RDFTest):
    suffix = rdf_test_uri.split("#")[1]
    if suffix in EXPECTED_FAILURES:
        pytest.xfail(EXPECTED_FAILURES[suffix])
    testers[type](rdf_test)
