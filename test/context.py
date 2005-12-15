import unittest

from tempfile import mkdtemp
from rdflib import *

class ContextTestCase(unittest.TestCase):
    #backend = 'Memory'
    backend = 'default'

    def setUp(self):
        self.graph = Graph(backend=self.backend)        
        self.graph.open(mkdtemp())
        self.michel = URIRef(u'michel')
        self.tarek = URIRef(u'tarek')
        self.bob = URIRef(u'bob')
        self.likes = URIRef(u'likes')
        self.hates = URIRef(u'hates')
        self.pizza = URIRef(u'pizza')
        self.cheese = URIRef(u'cheese')

        self.c1 = URIRef(u'context-1')
        self.c2 = URIRef(u'context-2')

        # delete the graph for each test!
        self.graph.remove((None, None, None))

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
        c1 = self.c1

        self.graph.add((tarek, likes, pizza), c1)
        self.graph.add((tarek, likes, cheese), c1)
        self.graph.add((michel, likes, pizza), c1)
        self.graph.add((michel, likes, cheese), c1)
        self.graph.add((bob, likes, cheese), c1)
        self.graph.add((bob, hates, pizza), c1)
        self.graph.add((bob, hates, michel), c1) # gasp!        

    def removeStuff(self):
        tarek = self.tarek
        michel = self.michel
        bob = self.bob
        likes = self.likes
        hates = self.hates
        pizza = self.pizza
        cheese = self.cheese
        c1 = self.c1

        self.graph.remove((tarek, likes, pizza), c1)
        self.graph.remove((tarek, likes, cheese), c1)
        self.graph.remove((michel, likes, pizza), c1)
        self.graph.remove((michel, likes, cheese), c1)
        self.graph.remove((bob, likes, cheese), c1)
        self.graph.remove((bob, hates, pizza), c1)
        self.graph.remove((bob, hates, michel), c1) # gasp!

    def addStuffInMultipleContexts(self):
        c1 = self.c1
        c2 = self.c2
        triple = (self.pizza, self.hates, self.tarek) # revenge!

        # add to default context
        self.graph.add(triple)
        # add to context 1
        self.graph.add(triple, c1)
        # add to context 2
        self.graph.add(triple, c2)

    def testAdd(self):
        self.addStuff()

    def testRemove(self):
        self.addStuff()
        self.removeStuff()

    def testLenInOneContext(self):
        c1 = self.c1
        oldLen = len(self.graph)
        # make sure context is empty

        self.graph.remove_context(c1)

        for i in range(0, 10):
            self.graph.add((BNode(), self.hates, self.hates), c1)
        self.assertEquals(len(self.graph), oldLen + 10)
        self.assertEquals(len(self.graph.get_context(c1)), oldLen + 10)
        self.graph.remove_context(c1)
        self.assertEquals(len(self.graph), oldLen)

    def testLenInMultipleContexts(self):
        oldLen = len(self.graph)
        self.addStuffInMultipleContexts()
        # TODO: what should the length of the graph now be? 1 or 3?
        #self.assertEquals(len(self.graph), oldLen + 1)

    def testRemoveInMultipleContexts(self):
        c1 = self.c1
        c2 = self.c2
        triple = (self.pizza, self.hates, self.tarek) # revenge!

        self.addStuffInMultipleContexts()

        # triple should be still in store after removing it from c1 + c2
        self.assert_(triple in self.graph)
        self.graph.remove(triple, c1)
        self.assert_(triple in self.graph)
        self.graph.remove(triple, c2)
        self.assert_(triple in self.graph)
        self.graph.remove(triple)
        # now gone!
        self.assert_(triple not in self.graph)

        # add again and see if remove without context removes all triples!
        self.addStuffInMultipleContexts()
        self.graph.remove(triple)
        self.assert_(triple not in self.graph)

    def testContexts(self):
        triple = (self.pizza, self.hates, self.tarek) # revenge!

        self.addStuffInMultipleContexts()
        self.assert_(self.c1 in self.graph.contexts())
        self.assert_(self.c2 in self.graph.contexts())

        contextList = list(self.graph.contexts(triple))
        self.assert_(self.c1 in contextList)
        self.assert_(self.c2 in contextList)

    def testRemoveContext(self):
        c1 = self.c1

        self.addStuffInMultipleContexts()
        self.assertEquals(self.graph.__len__(context=c1), 1)

        self.graph.remove_context(c1)
        self.assert_(self.c1 not in self.graph.contexts())

    def testRemoveAny(self):
        Any = None
        self.addStuffInMultipleContexts()
        self.graph.remove((Any, Any, Any))
        self.assertEquals(len(self.graph), 0)

    def testTriples(self):
        tarek = self.tarek
        michel = self.michel
        bob = self.bob
        likes = self.likes
        hates = self.hates
        pizza = self.pizza
        cheese = self.cheese
        c1 = self.c1
        asserte = self.assertEquals
        triples = self.graph.triples
        graph = self.graph
        Any = None

        self.addStuff()

        # unbound subjects with context
        asserte(len(list(triples((Any, likes, pizza), c1))), 2)
        asserte(len(list(triples((Any, hates, pizza), c1))), 1)
        asserte(len(list(triples((Any, likes, cheese), c1))), 3)
        asserte(len(list(triples((Any, hates, cheese), c1))), 0)

        # unbound subjects without context, same results!
        asserte(len(list(triples((Any, likes, pizza)))), 2)
        asserte(len(list(triples((Any, hates, pizza)))), 1)
        asserte(len(list(triples((Any, likes, cheese)))), 3)
        asserte(len(list(triples((Any, hates, cheese)))), 0)

        # unbound objects with context
        asserte(len(list(triples((michel, likes, Any), c1))), 2)
        asserte(len(list(triples((tarek, likes, Any), c1))), 2)
        asserte(len(list(triples((bob, hates, Any), c1))), 2)
        asserte(len(list(triples((bob, likes, Any), c1))), 1)

        # unbound objects without context, same results!
        asserte(len(list(triples((michel, likes, Any)))), 2)
        asserte(len(list(triples((tarek, likes, Any)))), 2)
        asserte(len(list(triples((bob, hates, Any)))), 2)
        asserte(len(list(triples((bob, likes, Any)))), 1)

        # unbound predicates with context
        asserte(len(list(triples((michel, Any, cheese), c1))), 1)
        asserte(len(list(triples((tarek, Any, cheese), c1))), 1)
        asserte(len(list(triples((bob, Any, pizza), c1))), 1)
        asserte(len(list(triples((bob, Any, michel), c1))), 1)

        # unbound predicates without context, same results!
        asserte(len(list(triples((michel, Any, cheese)))), 1)
        asserte(len(list(triples((tarek, Any, cheese)))), 1)
        asserte(len(list(triples((bob, Any, pizza)))), 1)
        asserte(len(list(triples((bob, Any, michel)))), 1)

        # unbound subject, objects with context
        asserte(len(list(triples((Any, hates, Any), c1))), 2)
        asserte(len(list(triples((Any, likes, Any), c1))), 5)

        # unbound subject, objects without context, same results!
        asserte(len(list(triples((Any, hates, Any)))), 2)
        asserte(len(list(triples((Any, likes, Any)))), 5)

        # unbound predicates, objects with context
        asserte(len(list(triples((michel, Any, Any), c1))), 2)
        asserte(len(list(triples((bob, Any, Any), c1))), 3)
        asserte(len(list(triples((tarek, Any, Any), c1))), 2)   

        # unbound predicates, objects without context, same results!
        asserte(len(list(triples((michel, Any, Any)))), 2)
        asserte(len(list(triples((bob, Any, Any)))), 3)
        asserte(len(list(triples((tarek, Any, Any)))), 2)      

        # unbound subjects, predicates with context
        asserte(len(list(triples((Any, Any, pizza), c1))), 3)
        asserte(len(list(triples((Any, Any, cheese), c1))), 3)
        asserte(len(list(triples((Any, Any, michel), c1))), 1)  

        # unbound subjects, predicates without context, same results!
        asserte(len(list(triples((Any, Any, pizza)))), 3)
        asserte(len(list(triples((Any, Any, cheese)))), 3)
        asserte(len(list(triples((Any, Any, michel)))), 1)        

        # all unbound with context
        asserte(len(list(triples((Any, Any, Any), c1))), 7)
        # all unbound without context, same result!
        asserte(len(list(triples((Any, Any, Any)))), 7)

        for c in [graph, graph.get_context(c1)]:
            # unbound subjects
            #c = graph.get_context(c1)
            asserte(set(c.subjects(likes, pizza)), set((michel, tarek)))
            asserte(set(c.subjects(hates, pizza)), set((bob,)))
            asserte(set(c.subjects(likes, cheese)), set([tarek, bob, michel]))
            asserte(set(c.subjects(hates, cheese)), set())

            # unbound objects
            asserte(set(c.objects(michel, likes)), set([cheese, pizza]))
            asserte(set(c.objects(tarek, likes)), set([cheese, pizza]))
            asserte(set(c.objects(bob, hates)), set([michel, pizza]))
            asserte(set(c.objects(bob, likes)), set([cheese]))

            # unbound predicates
            asserte(set(c.predicates(michel, cheese)), set([likes]))
            asserte(set(c.predicates(tarek, cheese)), set([likes]))
            asserte(set(c.predicates(bob, pizza)), set([hates]))
            asserte(set(c.predicates(bob, michel)), set([hates]))

            asserte(set(c.subject_objects(hates)), set([(bob, pizza), (bob, michel)]))
            asserte(set(c.subject_objects(likes)), set([(tarek, cheese), (michel, cheese), (michel, pizza), (bob, cheese), (tarek, pizza)]))

            asserte(set(c.predicate_objects(michel)), set([(likes, cheese), (likes, pizza)]))
            asserte(set(c.predicate_objects(bob)), set([(likes, cheese), (hates, pizza), (hates, michel)]))
            asserte(set(c.predicate_objects(tarek)), set([(likes, cheese), (likes, pizza)]))
            
            asserte(set(c.subject_predicates(pizza)), set([(bob, hates), (tarek, likes), (michel, likes)]))
            asserte(set(c.subject_predicates(cheese)), set([(bob, likes), (tarek, likes), (michel, likes)]))
            asserte(set(c.subject_predicates(michel)), set([(bob, hates)]))

            asserte(set(c), set([(bob, hates, michel), (bob, likes, cheese), (tarek, likes, pizza), (michel, likes, pizza), (michel, likes, cheese), (bob, hates, pizza), (tarek, likes, cheese)]))

        # remove stuff and make sure the graph is empty again
        self.removeStuff()
        asserte(len(list(triples((Any, Any, Any), c1))), 0)
        asserte(len(list(triples((Any, Any, Any)))), 0)

class IOMemoryContextTestCase(ContextTestCase):
    backend = "IOMemory"

try:
    from rdflib.store.Sleepycat import Sleepycat
    class SleepycatStoreTestCase(ContextTestCase):
        backend = "Sleepycat"
except ImportError, e:
    print "Can not test Sleepycat store:", e

try:
    import persistent
    # If we can import persistent then test ZODB backend
    class ZODBContextTestCase(ContextTestCase):
        backend = "ZODB"
except ImportError:
    pass

try:
    import backends.Sleepycat
except ImportError:
    del ContextTestCase

if __name__ == '__main__':
    unittest.main()    
