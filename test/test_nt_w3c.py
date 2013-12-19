"""This runs the nt tests for the W3C RDF Working Group's N-Quads
test suite."""

from rdflib import Graph
from manifest import nose_tests, RDFT


def nt(test):
    g = Graph()

    try:
        g.parse(test.action, format='nt')
        if not test.syntax:
            raise AssertionError("Input shouldn't have parsed!")
    except:
        if test.syntax:
            raise

testers = {
    RDFT.TestNTriplesPositiveSyntax: nt,
    RDFT.TestNTriplesNegativeSyntax: nt
}

def test_nt():
    for t in nose_tests(testers, 'test/w3c/nt/manifest.ttl'):
        yield t


if __name__ == '__main__':
    pass
