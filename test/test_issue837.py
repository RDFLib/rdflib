from fractions import Fraction

from rdflib import Graph, ConjunctiveGraph, Literal, URIRef
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

    def tearDown(self):
        self.graph.close()

    def addStuff(self):
        tarek = self.tarek
        michel = self.michel
        bob = self.bob
        likes = self.likes
        hates = self.hates
        pizza = self.pizza
        cheese = self.cheese

        self.graph.add((tarek, likes, pizza))
        self.graph.add((tarek, likes, cheese))
        self.graph.add((tarek, likes, bob))
        self.graph.add((michel, likes, pizza))
        self.graph.add((michel, likes, cheese))
        self.graph.add((bob, likes, cheese))
        self.graph.add((bob, hates, pizza))
        self.graph.add((bob, hates, michel))

    def testSubjects(self):
        asserte = self.assertEqual
        self.addStuff()
        asserte(len([sub for sub in self.graph.subjects()]), 3)

    def testPredicates(self):
        asserte = self.assertEqual
        self.addStuff()
        asserte(len([pred for pred in self.graph.predicates()]), 2)

    def testObjects(self):
        asserte = self.assertEqual
        self.addStuff()
        asserte(len([obj for obj in self.graph.objects()]), 4)


if __name__ == "__main__":
    unittest.main()
