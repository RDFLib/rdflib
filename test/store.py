import unittest

from rdflib import URIRef, BNode, Literal
from rdflib.store.Memory import Memory

from random import random
from tempfile import mkdtemp

def random_uri():
    return URIRef("%s" % random())


class StoreTestCase(unittest.TestCase):
    """
    Test case for testing store performance... probably should be
    something other than a unit test... but for now we'll add it as a
    unit test.
    """
    store_class = Memory
    configuration = None

    def setUp(self):
        self.store = self.store_class(configuration=mkdtemp())
        s = random_uri()
        p = random_uri()
        o = random_uri()
        self.t1 = (s, p, o)
        self.c1 = random_uri()


    def tearDown(self):
        del self.store

    def testTriples(self):
        self.store.add(self.t1, self.c1)
        num = len(list(self.store.triples((None, None, None))))
        self.assert_(num==1)
        for (s, p, o), c in self.store.triples((None, None, None)):
            if self.store.context_aware:
                self.assert_(set(c)==set([self.c1]))
            else:
                self.assert_(set(c)==set())

    def testContexts(self):
        store = self.store
        if store.context_aware:
            store.contexts()
            store.contexts(self.t1)
            self.store.add(self.t1, self.c1)
            self.assert_(len(store)==1)
            #store.remove(self.t1, None)
            store.remove(self.t1, self.c1)
            #store.remove_context(self.c1)
            self.assert_(len(store)==0)
            
try:
    from rdflib.store.Sleepycat import Sleepycat
    class SleepycatStoreTestCase(StoreTestCase):
        store_class = Sleepycat
        configuration = mkdtemp()

except ImportError, e:
    print "Can not test Sleepycat store:", e


if __name__ == '__main__':
    unittest.main()    
