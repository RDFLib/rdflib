"""This runs the nt tests for the W3C RDF Working Group's N-Quads
test suite."""
import os

from rdflib import Graph
from test import TEST_DIR
from test.manifest import nose_tests, RDFT

from test.testutils import nose_tst_earl_report

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


testers = {RDFT.TestNTriplesPositiveSyntax: nt, RDFT.TestNTriplesNegativeSyntax: nt}


def test_nt(tests=None):
    manifest_file = os.path.join(TEST_DIR, "w3c/nt/manifest.ttl")
    for t in nose_tests(testers, manifest_file, legacy=True):
        if tests:
            for test in tests:
                if test in t[1].uri:
                    break
            else:
                continue

        yield t


if __name__ == "__main__":
    verbose = True

    nose_tst_earl_report(test_nt, "rdflib_nt")
