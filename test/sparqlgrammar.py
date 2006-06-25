import unittest

from rdflib import *

class SPARQLGrammarTestCase(unittest.TestCase):

    def setUp(self):
        self.p = parser.SPARQLGrammar()

    def test_VAR_(self):
        self.p._VAR_.parseString('?bob') == ['?bob']

    def testURI(self):
        self.p.URI.parseString('<dc:title>') == ['?bob']

if __name__ == '__main__':
    unittest.main()    
