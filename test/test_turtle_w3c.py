"""This runs the turtle tests for the W3C RDF Working Group's N-Quads
test suite."""

from rdflib import Graph
from manifest import nose_tests, RDFT


def turtle(test):
    g = Graph()

    try:
        g.parse(test.action, format='turtle')
        if not test.syntax:
            raise AssertionError("Input shouldn't have parsed!")
    except:
        if test.syntax:
            raise

testers = {
    RDFT.TestTurtlePositiveSyntax: turtle,
    RDFT.TestTurtleNegativeSyntax: turtle
}

def test_turtle(tests = None):
    for t in nose_tests(testers, 'test/w3c/turtle/manifest.ttl'):
        if tests:
            for test in tests:
                if test in t[1].uri: break
            else:
                continue

        yield t


if __name__ == '__main__':

    from optparse import OptionParser
    p = OptionParser()
    (options, args) = p.parse_args()

    for t in test_turtle(args):
        print 'Running ', t[1].uri
        t[0](t[1])
