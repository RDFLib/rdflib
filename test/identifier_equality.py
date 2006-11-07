import unittest

from rdflib import URIRef, BNode, Literal

from rdflib.syntax.parsers.RDFXMLHandler import CORE_SYNTAX_TERMS

from rdflib.Graph import Graph
from rdflib import RDF

class IdentifierEquality(unittest.TestCase):

    def setUp(self):
        self.uriref = URIRef("http://example.org/")
        self.bnode = BNode()
        self.literal = Literal("http://example.org/")
        self.python_literal = u"http://example.org/"
        self.python_literal_2 = u"foo"

    def testA(self):
        self.assertEquals(self.uriref==self.literal, False)

    def testB(self):
        self.assertEquals(self.literal==self.uriref, False)

    def testC(self):
        self.assertEquals(self.uriref==self.python_literal, False)

    def testD(self):
        self.assertEquals(self.python_literal==self.uriref, False)

    def testE(self):
        self.assertEquals(self.literal==self.python_literal, True)

    def testF(self):
        self.assertEquals(self.python_literal==self.literal, True)

    def testG(self):
        self.assertEquals("foo" in CORE_SYNTAX_TERMS, False)

    def testH(self):
        self.assertEquals(URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#RDF") in CORE_SYNTAX_TERMS, True)

    def testI(self):
        g = Graph()
        g.add((self.uriref, RDF.value, self.literal))
        g.add((self.uriref, RDF.value, self.uriref))
        self.assertEqual(len(g), 2)


if __name__ == "__main__":
    unittest.main()


