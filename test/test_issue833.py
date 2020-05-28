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

    def testAdd(self):
        asserte = self.assertEqual
        tarek = self.tarek
        likes = self.likes
        cheese = self.cheese

        # New triple
        added = self.graph.add((tarek,likes,cheese))
        asserte(added,1)
        # Duplicate Triple
        added = self.graph.add((tarek,likes,cheese))
        asserte(added,0)

    def testAddN(self):
        asserte = self.assertEqual
        tarek = self.tarek
        bob = self.bob
        likes = self.likes
        hates = self.hates
        pizza = self.pizza
        cheese = self.cheese
        self.prepareQuadsList()
        count = self.graph.addN(self.quads)
        asserte(count,5)

        self.quads = []
        # Duplicate Triple
        self.quads.append((tarek, likes, pizza, self.graph))
        # New Triple 
        self.quads.append((bob, likes, tarek, self.graph))
        # Context not an instance of graph
        self.quads.append((bob, likes, cheese, ""))
        count = self.graph.addN(self.quads)
        asserte(count,1)

if __name__ == "__main__":
    unittest.main()
