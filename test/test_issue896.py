# test for https://github.com/RDFLib/rdflib/issues/896

from rdflib import Graph, URIRef
import unittest


class TestIssue837(unittest.TestCase):

    def setUp(self):
        self.graph = Graph()

        self.michel = URIRef(u'michel')
        self.tarek = URIRef(u'tarek')
        self.bob = URIRef(u'bob')
        self.likes = URIRef(u'likes')
        self.hates = URIRef(u'hates')
        self.pizza = URIRef(u'pizza')
        self.cheese = URIRef(u'cheese')

        self.triples = []

    def tearDown(self):
        self.graph.close()

    def prepareTriplesList(self):
        tarek = self.tarek
        michel = self.michel
        bob = self.bob
        likes = self.likes
        hates = self.hates
        pizza = self.pizza
        cheese = self.cheese

        self.triples.append((tarek, likes, pizza))
        self.triples.append((tarek, likes, cheese))
        self.triples.append((tarek, likes, bob))
        self.triples.append((bob, likes, cheese))
        self.triples.append((bob, hates, pizza))

    def testAddAll(self):
        asserte = self.assertEqual
        self.prepareTriplesList()
        self.graph.add_all(self.triples)
        asserte(len(self.graph),5)

    def testAddAllAssertion(self):
        self.prepareTriplesList()
        # Adding a triple that fails the assertion 
        tarek = self.tarek
        pizza = self.pizza
        self.triples.append((tarek,"loves",pizza))

        with self.assertRaises(AssertionError):
            self.graph.add_all(self.triples)

    def testAddAll1(self):
        asserte = self.assertEqual
        self.prepareTriplesList()
        # Adding a triple that fails the assertion at the 4th position
        tarek = self.tarek
        pizza = self.pizza
        self.triples.insert(3,(tarek,"loves",pizza))

        with self.assertRaises(AssertionError):
            # Changing function parameter all_or_none to False
            self.graph.add_all(self.triples, all_or_none=False)

        # Triples before the assertion should be added to the graph
        asserte(len(self.graph),3)

if __name__ == "__main__":
    unittest.main()
