import unittest

from rdflib import *
from rdflib.graph import Graph

class NTTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testModel(self):
        g = Graph()
        g.load("http://www.w3.org/2000/10/rdf-tests/rdfcore/rdfms-empty-property-elements/test002.nt", format="nt")


if __name__ == "__main__":
    unittest.main()
