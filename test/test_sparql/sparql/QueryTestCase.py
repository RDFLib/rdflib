import unittest

from rdflib.graph import Graph

class QueryTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testUnicodeString(self):
        from rdflib.sparql.parser import parse
        from cStringIO import StringIO

        q = \
          u"""
          PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
          SELECT ?pred
          WHERE { rdf:foobar rdf:predicate ?pred. }
          """ 

        p = parse(q)

if __name__ == '__main__':
    unittest.main()

