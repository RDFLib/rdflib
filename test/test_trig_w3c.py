"""Runs the tests for the W3C RDF Working Group's TriG test suite.

"""

from rdflib import Graph
from manifest import nose_tests, RDFT
from testutils import nose_tst_earl_report


def trig(test):
    g = Graph()

    try:
        g.parse(test.action, format='trig')
        if not test.syntax:
            raise AssertionError("Input shouldn't have parsed!")
    except:
        if test.syntax:
            raise

testers = {
    RDFT.TestTrigPositiveSyntax: trig,
    RDFT.TestTrigNegativeSyntax: trig
}

def test_trig(tests):
    for t in nose_tests(testers, 'test/w3c/trig/manifest.ttl'):
        if tests:
            for test in tests:
                if test in t[1].uri: break
            else:
                continue

        yield t


if __name__ == '__main__':
    verbose = True

    nose_tst_earl_report(test_trig, 'rdflib_trig')
