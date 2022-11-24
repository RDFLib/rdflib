"""This runs the nt tests for the W3C RDF Working Group's N-Quads
test suite."""
import itertools
import os
from test.data import TEST_DATA_DIR
from test.utils.manifest import RDFTest, read_manifest
from test.utils.namespace import RDFT
from typing import Callable, Dict

import pytest

from rdflib import Graph
from rdflib.compare import graph_diff, isomorphic
from rdflib.namespace import split_uri
from rdflib.term import Node, URIRef

verbose = False


def n3(test: RDFTest):
    g = Graph()

    try:

        base = "https://w3c.github.io/N3/tests/N3Tests/" + split_uri(test.action)[1]

        g.parse(test.action, publicID=base, format="n3")
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
    RDFT.TestTurtlePositiveSyntax: n3,
    RDFT.TestTurtleNegativeSyntax: n3,
    RDFT.TestTurtleEval: n3,
    RDFT.TestTurtleNegativeEval: n3,
}


turtle_eval_skipped = [
    "SPARQL_style_prefix",
    "SPARQL_style_base",
    "LITERAL1",
    "LITERAL1_ascii_boundaries",
    "LITERAL1_with_UTF8_boundaries",
    "LITERAL1_all_controls",
    "LITERAL1_all_punctuation",
    "LITERAL_LONG1",
    "LITERAL_LONG1_ascii_boundaries",
    "LITERAL_LONG1_with_UTF8_boundaries",
    "LITERAL_LONG1_with_1_squote",
    "LITERAL_LONG1_with_2_squotes",
    "literal_with_CHARACTER_TABULATION",
    "literal_with_BACKSPACE",
    "literal_with_LINE_FEED",
    "literal_with_CARRIAGE_RETURN",
    "literal_with_FORM_FEED",
    "literal_with_REVERSE_SOLIDUS",
    "literal_with_escaped_CHARACTER_TABULATION",
    "literal_with_escaped_BACKSPACE",
    "literal_with_escaped_LINE_FEED",
    "literal_with_escaped_CARRIAGE_RETURN",
    "literal_with_escaped_FORM_FEED",
    "literal_with_numeric_escape4",
    "literal_with_numeric_escape8",
    "turtle-subm-01",
    "turtle-subm-27",
]


turtle_positive_syntax_skipped = [
    "turtle-syntax-base-02",
    "turtle-syntax-base-04",
    "turtle-syntax-prefix-02",
    "turtle-syntax-prefix-03",
    "turtle-syntax-string-04",
    "turtle-syntax-string-05",
    "turtle-syntax-string-06",
    "turtle-syntax-string-09",
    "turtle-syntax-string-11",
]

EXPECTED_FAILURES: Dict[str, str] = {}

if os.name == "nt":
    for test in ["turtle-subm-15", "turtle-subm-16"]:
        EXPECTED_FAILURES[test] = "Issue with nt parser and line endings on windows"

for test in turtle_eval_skipped + turtle_positive_syntax_skipped:
    EXPECTED_FAILURES[test] = "Known issue with Turtle parser"


@pytest.mark.parametrize(
    "rdf_test_uri, type, rdf_test",
    itertools.chain(
        *(
            read_manifest(
                os.path.join(TEST_DATA_DIR, "suites", f"w3c/n3/{manifest}"), legacy=True
            )
            for manifest in [
                "TurtleTests/manifest.ttl",
                "N3Tests/manifest-parser.ttl",
                # "N3Tests/manifest-reasoner.ttl",
                # "N3Tests/manifest-extended.ttl",
            ]
        )
    ),
)
def test_manifest(rdf_test_uri: URIRef, type: Node, rdf_test: RDFTest):
    suffix = rdf_test_uri.split("#")[1]
    if suffix in EXPECTED_FAILURES:
        pytest.xfail(EXPECTED_FAILURES[suffix])
    testers[type](rdf_test)
