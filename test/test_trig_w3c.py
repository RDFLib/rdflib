"""Runs the tests for the W3C RDF Working Group's TriG test suite.

"""

from rdflib import ConjunctiveGraph
from rdflib.compare import graph_diff, isomorphic

from manifest import nose_tests, RDFT
from testutils import nose_tst_earl_report


def trig(test):
    g = ConjunctiveGraph()

    try:
        g.parse(test.action, format='trig')
        if not test.syntax:
            raise AssertionError("Input shouldn't have parsed!")

        if test.result: # eval test
            res = ConjunctiveGraph()
            res.parse(test.result, format='nquads')

            if verbose:
                both, first, second = graph_diff(g,res)
                if not first and not second: return
                print "Diff:"
                #print "%d triples in both"%len(both)
                print "TriG Only:"
                for t in first:
                    print t

                print "--------------------"
                print "NQuads Only"
                for t in second:
                    print t
                raise Exception('Graphs do not match!')

            assert isomorphic(g, res), 'graphs must be the same'

    except:
        if test.syntax:
            raise

testers = {
    RDFT.TestTrigPositiveSyntax: trig,
    RDFT.TestTrigNegativeSyntax: trig,
#    RDFT.TestTrigEval: trig,
    RDFT.TestTrigNegativeEval: trig
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
