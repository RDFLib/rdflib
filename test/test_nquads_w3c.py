"""This runs the nquads tests for the W3C RDF Working Group's N-Quads
test suite."""

from rdflib import Graph
from manifest import nose_tests, RDFT


def nquads(test):
    g = Graph()

    try:
        g.parse(test.action, format='nquads')
        if not test.syntax:
            raise AssertionError("Input shouldn't have parsed!")
    except:
        if test.syntax:
            raise

testers = {
    RDFT.TestNQuadsPositiveSyntax: nquads,
    RDFT.TestNQuadsNegativeSyntax: nquads
}

def test_nquads():
    for t in nose_tests(testers, 'test/w3c/nquads/manifest.ttl'):
        yield t


if __name__ == '__main__':
    pass
