#!/usr/bin/python
#
# test.py - RDFa Test Suite
#

import os, sys, string
import rdfdiff
import unittest
import ntriples

from rdfdiff import Graph
from rdflib import ConjunctiveGraph as RGraph
from rdflib import StringInputSource
from rdflib import URIRef
from rdflib import BNode
from rdflib import Literal


def main():
    suite = unittest.TestSuite()
    for test in make_cases():
        suite.addTest(test)
    print "\n------\nRDFa Parser Tests\n-----\n"
    unittest.TextTestRunner(verbosity=2,descriptions=1).run(suite)


def make_cases():
    testdir = "test/rdfa"
    verbose = False
    tests = [os.path.splitext(f)[0]
      for f in os.listdir(testdir)
      if os.path.splitext(f)[1] == ".htm" ]
    tests.sort()
    for testname in tests:
        yield RDFaTestStub(os.path.abspath(os.path.join(testdir,testname)))


# expose each test for e.g. Nose to run
def all_tests():
    for test in make_cases():
        yield test.runTest,


class RDFaTestStub(unittest.TestCase):

    def __init__(self, testbase):
        unittest.TestCase.__init__(self)
        self.testbase = testbase
        self.pubId = 'http://example.com/'

    def shortDescription(self):
        return str(os.path.basename(self.testbase))

    def nodeToString(self, node):
        if isinstance(node, BNode):
            bid = node.n3()
            if(bid[0:4] == '_:_:'):
                    bid = bid[2:]
            return ntriples.bNode(str(bid))
        elif isinstance(node, URIRef):
            if len(str(node)) == 0:
                    return ntriples.URI(self.pubId)
            return ntriples.URI(str(node))
        elif isinstance(node, Literal):
            return ntriples.Literal(str(node), lang= node.language or None,
                    dtype= node.datatype  or None)

    def runTest(self):
        testfile = self.testbase + ".htm"
        resultsf = self.testbase + ".ttl"
        self.failIf(not os.path.isfile(resultsf), "missing expected results file.")

        store1 = RGraph()
        store1.load(resultsf, publicID=self.pubId, format="n3")
        pcontents = store1.serialize(format='nt')
        pg = Graph()
        for a, b, c in store1:
            pg.triples.add(tuple(map(self.nodeToString, (a,b,c))))
            #print tuple(map(self.nodeToString, (a,b,c)))

        store2 = RGraph()
        store2.load(testfile, publicID=self.pubId, format="rdfa")
        qcontents = store2.serialize(format='nt')
        qg = Graph()
        for a, b, c in store2:
            qg.triples.add(tuple(map(self.nodeToString, (a,b,c))))

        self.failIf(not hash(pg) == hash(qg),
                "In %s: results do not match.\n%s\n\n%s" % (self.shortDescription(), pcontents, qcontents))


if __name__ == '__main__':
    main()


