import unittest

# you must export your PYTHONPATH to point to a Z3 installation to get this to work!, like:
# export PYTHONPATH="export PYTHONPATH="/home/michel/dev/Zope3Trunk/src"

from rdflib import *
from rdflib.backends.ZODB import ZODB
from rdflib.constants import RDFS_LABEL

class ZODBTestCase(unittest.TestCase):

    def setUp(self):
        self.store = Graph(backend=ZODB())
        self.michel = URIRef(u'michel')
        self.tarek = URIRef(u'tarek')
        self.bob = URIRef(u'bob')
        self.likes = URIRef(u'likes')
        self.hates = URIRef(u'hates')
        self.pizza = URIRef(u'pizza')
        self.cheese = URIRef(u'cheese')

    def addStuff(self):
        tarek = self.tarek
        michel = self.michel
        bob = self.bob
        likes = self.likes
        hates = self.hates
        pizza = self.pizza
        cheese = self.cheese

        self.store.add(Triple(tarek, likes, pizza))
        self.store.add(Triple(tarek, likes, cheese))
        self.store.add(Triple(michel, likes, pizza))
        self.store.add(Triple(michel, likes, cheese))
        self.store.add(Triple(bob, likes, cheese))
        self.store.add(Triple(bob, hates, pizza))
        self.store.add(Triple(bob, hates, michel)) # gasp!        

    def removeStuff(self):
        tarek = self.tarek
        michel = self.michel
        bob = self.bob
        likes = self.likes
        hates = self.hates
        pizza = self.pizza
        cheese = self.cheese

        self.store.remove(Triple(tarek, likes, pizza))
        self.store.remove(Triple(tarek, likes, cheese))
        self.store.remove(Triple(michel, likes, pizza))
        self.store.remove(Triple(michel, likes, cheese))
        self.store.remove(Triple(bob, likes, cheese))
        self.store.remove(Triple(bob, hates, pizza))
        self.store.remove(Triple(bob, hates, michel)) # gasp!

    def testAdd(self):
        self.addStuff()

    def testRemove(self):
        self.addStuff()
        self.removeStuff()

    def testTriples(self):
        tarek = self.tarek
        michel = self.michel
        bob = self.bob
        likes = self.likes
        hates = self.hates
        pizza = self.pizza
        cheese = self.cheese
        asserte = self.assertEquals
        triples = self.store.triples
        Any = None

        self.addStuff()

        # unbound subjects
        asserte(len(list(triples(Triple(Any, likes, pizza)))), 2)
        asserte(len(list(triples(Triple(Any, hates, pizza)))), 1)
        asserte(len(list(triples(Triple(Any, likes, cheese)))), 3)
        asserte(len(list(triples(Triple(Any, hates, cheese)))), 0)

        # unbound objects
        asserte(len(list(triples(Triple(michel, likes, Any)))), 2)
        asserte(len(list(triples(Triple(tarek, likes, Any)))), 2)
        asserte(len(list(triples(Triple(bob, hates, Any)))), 2)
        asserte(len(list(triples(Triple(bob, likes, Any)))), 1)

        # unbound predicates
        asserte(len(list(triples(Triple(michel, Any, cheese)))), 1)
        asserte(len(list(triples(Triple(tarek, Any, cheese)))), 1)
        asserte(len(list(triples(Triple(bob, Any, pizza)))), 1)
        asserte(len(list(triples(Triple(bob, Any, michel)))), 1)

        # unbound subject, objects
        asserte(len(list(triples(Triple(Any, hates, Any)))), 2)
        asserte(len(list(triples(Triple(Any, likes, Any)))), 5)

        # unbound predicates, objects
        asserte(len(list(triples(Triple(michel, Any, Any)))), 2)
        asserte(len(list(triples(Triple(bob, Any, Any)))), 3)
        asserte(len(list(triples(Triple(tarek, Any, Any)))), 2)        

        # unbound subjects, predicates
        asserte(len(list(triples(Triple(Any, Any, pizza)))), 3)
        asserte(len(list(triples(Triple(Any, Any, cheese)))), 3)
        asserte(len(list(triples(Triple(Any, Any, michel)))), 1)        

        # all unbound
        asserte(len(list(triples(Triple(Any, Any, Any)))), 7)
        self.removeStuff()
        asserte(len(list(triples(Triple(Any, Any, Any)))), 0)

def test_suite():
    return unittest.makeSuite(ZODBTestCase)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
