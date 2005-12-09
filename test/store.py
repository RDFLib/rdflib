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
    backend = 'default'

    def setUp(self):
        self.gcold = gc.isenabled()
        gc.collect()
        gc.disable()
        self.store = Graph(backend=self.backend)
        path = a_tmp_dir = mkdtemp()
        self.store.open(path)

    def tearDown(self):
        self.store.close()
        if self.gcold:
            gc.enable()
        # TODO: delete a_tmp_dir
        del self.store

    def testTime(self):
        number = 3
        it = itertools.repeat(None, number)        
	for i in it:
	    self._testTime()
        print "."

    def _testTime(self):
        number = 1000
        store = self.store

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
        print self.backend, "%.3g" % (t1 - t0),


class MemoryStoreTestCase(StoreTestCase):
    backend = "Memory"

try:
    from rdflib.backends.Sleepycat import Sleepycat
    class SleepycatStoreTestCase(StoreTestCase):
        backend = "Sleepycat"
except ImportError, e:
    print "Can not test Sleepycat backend:", e

try:
    import persistent
    # If we can import persistent then test ZODB backend
    class ZODBStoreTestCase(StoreTestCase):
        backend = "ZODB"
except ImportError, e:
    print "Can not test ZODB backend:", e


try:
    from Ft import Rdf
    # If we can import RDF then test Redland backend
    class RedLandTestCase(StoreTestCase):
        backend = "fourthought"
except ImportError, e:
    print "Can not test Redland backend:", e    

try:
    import MySQLdb,sha,sys
    # If we can import RDF then test Redland backend
    class MySQLTestCase(StoreTestCase):
        backend = "MySQL"
except ImportError, e:
    print "Can not test MySQL backend:", e    

if __name__ == '__main__':
    unittest.main()    
