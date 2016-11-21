"""This runs the nquads tests for the W3C RDF Working Group's N-Quads
test suite."""

from rdflib import ConjunctiveGraph
from .manifest import nose_tests, RDFT

from .testutils import nose_tst_earl_report

verbose = False

def nquads(test):
    g = ConjunctiveGraph()

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

def test_nquads(tests = None):
    for t in nose_tests(testers, 'test/w3c/nquads/manifest.ttl'):
        if tests:
            for test in tests:
                if test in t[1].uri: break
            else:
                continue

        yield t


if __name__ == '__main__':
    verbose = True

    nose_tst_earl_report(test_nquads, 'rdflib_nquads')
