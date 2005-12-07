import unittest

from tempfile import mkdtemp

from rdflib import *
from rdflib.Graph import Graph

class GraphTestCase(unittest.TestCase):
    backend = 'default'
    path = None
    graph_class = Graph

    def setUp(self):
        self.store = self.graph_class(backend=self.backend)
        a_tmp_dir = mkdtemp()
        self.path = self.path or a_tmp_dir
        self.store.open(self.path)

        self.michel = URIRef(u'michel')
        self.tarek = URIRef(u'tarek')
        self.bob = URIRef(u'bob')
        self.likes = URIRef(u'likes')
        self.hates = URIRef(u'hates')
        self.pizza = URIRef(u'pizza')
        self.cheese = URIRef(u'cheese')

    def tearDown(self):
        self.store.close()

    def addStuff(self):
        tarek = self.tarek
        michel = self.michel
        bob = self.bob
        likes = self.likes
        hates = self.hates
        pizza = self.pizza
        cheese = self.cheese

        self.store.add((tarek, likes, pizza))
        self.store.add((tarek, likes, cheese))
        self.store.add((michel, likes, pizza))
        self.store.add((michel, likes, cheese))
        self.store.add((bob, likes, cheese))
        self.store.add((bob, hates, pizza))
        self.store.add((bob, hates, michel)) # gasp!        

    def removeStuff(self):
        tarek = self.tarek
        michel = self.michel
        bob = self.bob
        likes = self.likes
        hates = self.hates
        pizza = self.pizza
        cheese = self.cheese

        self.store.remove((tarek, likes, pizza))
        self.store.remove((tarek, likes, cheese))
        self.store.remove((michel, likes, pizza))
        self.store.remove((michel, likes, cheese))
        self.store.remove((bob, likes, cheese))
        self.store.remove((bob, hates, pizza))
        self.store.remove((bob, hates, michel)) # gasp!

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
        asserte(len(list(triples((Any, likes, pizza)))), 2)
        asserte(len(list(triples((Any, hates, pizza)))), 1)
        asserte(len(list(triples((Any, likes, cheese)))), 3)
        asserte(len(list(triples((Any, hates, cheese)))), 0)

        # unbound objects
        asserte(len(list(triples((michel, likes, Any)))), 2)
        asserte(len(list(triples((tarek, likes, Any)))), 2)
        asserte(len(list(triples((bob, hates, Any)))), 2)
        asserte(len(list(triples((bob, likes, Any)))), 1)

        # unbound predicates
        asserte(len(list(triples((michel, Any, cheese)))), 1)
        asserte(len(list(triples((tarek, Any, cheese)))), 1)
        asserte(len(list(triples((bob, Any, pizza)))), 1)
        asserte(len(list(triples((bob, Any, michel)))), 1)

        # unbound subject, objects
        asserte(len(list(triples((Any, hates, Any)))), 2)
        asserte(len(list(triples((Any, likes, Any)))), 5)

        # unbound predicates, objects
        asserte(len(list(triples((michel, Any, Any)))), 2)
        asserte(len(list(triples((bob, Any, Any)))), 3)
        asserte(len(list(triples((tarek, Any, Any)))), 2)        

        # unbound subjects, predicates
        asserte(len(list(triples((Any, Any, pizza)))), 3)
        asserte(len(list(triples((Any, Any, cheese)))), 3)
        asserte(len(list(triples((Any, Any, michel)))), 1)        

        # all unbound
        asserte(len(list(triples((Any, Any, Any)))), 7)
        self.removeStuff()
        asserte(len(list(triples((Any, Any, Any)))), 0)

class MemoryGraphTestCase(GraphTestCase):
    backend = "Memory"
    graph_class = Graph

try:
    from rdflib.backends.Sleepycat import Sleepycat
    class SleepycatGraphTestCase(GraphTestCase):
        backend = "Sleepycat"
except ImportError, e:
    print "Can not test Sleepycat backend:", e

try:
    import persistent
    # If we can import persistent then test ZODB backend
    class ZODBGraphTestCase(GraphTestCase):
        backend = "ZODB"
except ImportError, e:
    print "Can not test ZODB backend:", e


try:
    import RDF
    # If we can import RDF then test Redland backend
    class RedLandTestCase(GraphTestCase):
        backend = "Redland"
except ImportError, e:
    print "Can not test Redland backend:", e    

if __name__ == '__main__':
    unittest.main()    
