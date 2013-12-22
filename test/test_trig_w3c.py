"""Runs the tests for the W3C RDF Working Group's TriG test suite.

"""

from rdflib import Graph
from manifest import nose_tests, RDFT


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

def test_trig():
    for t in nose_tests(testers, 'test/w3c/trig/manifest.ttl'):
        yield t


if __name__ == '__main__':
    pass
