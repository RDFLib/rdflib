# test for https://github.com/RDFLib/rdflib/issues/833

from rdflib import Graph, URIRef
import unittest


class TestIssue833(unittest.TestCase):

    def setUp(self):
        self.graph = Graph()

        self.tarek = URIRef(u'tarek')
        self.bob = URIRef(u'bob')
        self.likes = URIRef(u'likes')
        self.hates = URIRef(u'hates')
        self.pizza = URIRef(u'pizza')
        self.cheese = URIRef(u'cheese')

        self.quads = []

    def tearDown(self):
        self.graph.close()

    def prepareQuadsList(self):
        tarek = self.tarek
        bob = self.bob
        likes = self.likes
        hates = self.hates
        pizza = self.pizza
        cheese = self.cheese

        self.quads.append((tarek, likes, pizza, self.graph))
        self.quads.append((tarek, likes, cheese, self.graph))
        self.quads.append((tarek, likes, bob, self.graph))
        self.quads.append((bob, likes, cheese, self.graph))
        self.quads.append((bob, hates, pizza, self.graph))

    def testAddN(self):
        self.prepareQuadsList()
        count = self.graph.addN(self.quads)
        self.assertEqual(count,5)

        self.quads = []
        # Duplicate Triple
        self.quads.append((self.tarek, self.likes, self.pizza, self.graph))
        # New Triple 
        self.quads.append((self.bob, self.likes, self.tarek, self.graph))
        # Context not an instance of graph
        self.quads.append((self.bob, self.likes, self.cheese, ""))
        count = self.graph.addN(self.quads)
        self.assertEqual(count,1)

if __name__ == "__main__":
    unittest.main()
