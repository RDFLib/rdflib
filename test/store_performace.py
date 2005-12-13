import unittest

from rdflib.Graph import Graph
from rdflib import URIRef

import gc
import itertools
from time import time
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
    store = 'default'

    def setUp(self):
        self.gcold = gc.isenabled()
        gc.collect()
        gc.disable()
        self.graph = Graph(store=self.store)
        path = a_tmp_dir = mkdtemp()
        self.graph.open(path)

    def tearDown(self):
        self.graph.close()
        if self.gcold:
            gc.enable()
        # TODO: delete a_tmp_dir
        del self.graph

    def testTime(self):
        number = 3
        it = itertools.repeat(None, number)        
        for i in it:
            self._testTime()
        print "."

    def _testTime(self):
        number = 1000
        store = self.graph

        def add_random():
            s = random_uri()
            p = random_uri()
            o = random_uri()
            store.add((s, p, o))

        it = itertools.repeat(None, number)
        t0 = time()
        for _i in it:
            add_random()
        t1 = time()
        print self.store, "%.3g" % (t1 - t0),


class MemoryStoreTestCase(StoreTestCase):
    store = "Memory"

try:
    from rdflib.store.Sleepycat import Sleepycat
    class SleepycatStoreTestCase(StoreTestCase):
        store = "Sleepycat"
except ImportError, e:
    print "Can not test Sleepycat store:", e

try:
    import persistent
    # If we can import persistent then test ZODB store
    class ZODBStoreTestCase(StoreTestCase):
        store = "ZODB"
except ImportError, e:
    print "Can not test ZODB store:", e


try:
    import RDF
    # If we can import RDF then test Redland store
    class RedLandTestCase(StoreTestCase):
        store = "fourthought"
except ImportError, e:
    print "Can not test Redland store:", e    

# TODO: add test case for 4Suite backends?  from Ft import Rdf

try:
    import MySQLdb,sha,sys
    # If we can import RDF then test Redland store
    class MySQLTestCase(StoreTestCase):
        store = "MySQL"
except ImportError, e:
    print "Can not test MySQL store:", e    

if __name__ == '__main__':
    unittest.main()    
