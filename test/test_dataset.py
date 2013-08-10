import sys
import os
import unittest

from tempfile import mkdtemp, mkstemp
import shutil
from rdflib import Graph, Dataset, URIRef, BNode, plugin
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID

from nose.exc import SkipTest


class DatasetTestCase(unittest.TestCase):
    store = 'default'
    slow = True
    tmppath = None

    def setUp(self):
        try:
            self.graph = Dataset(store=self.store)
        except ImportError:
            raise SkipTest(
                "Dependencies for store '%s' not available!" % self.store)
        if self.store == "SQLite":
            _, self.tmppath = mkstemp(
                prefix='test', dir='/tmp', suffix='.sqlite')
        else:
            self.tmppath = mkdtemp()
        self.graph.open(self.tmppath, create=True)
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
        if os.path.isdir(self.tmppath):
            shutil.rmtree(self.tmppath)
        else:
            os.remove(self.tmppath)


    def testGraphAware(self): 
        if not self.graph.store.graph_aware: return 
        
        g = self.graph
        g1 = g.graph(self.c1)
        
        
        # added graph exists
        self.assertEquals(set(x.identifier for x in self.graph.contexts()), 
                          set([self.c1, DATASET_DEFAULT_GRAPH_ID]))

        # added graph is empty 
        self.assertEquals(len(g1), 0)
        
        g1.add( (self.tarek, self.likes, self.pizza) )

        # added graph still exists
        self.assertEquals(set(x.identifier for x in self.graph.contexts()), 
                          set([self.c1, DATASET_DEFAULT_GRAPH_ID]))

        # added graph contains one triple
        self.assertEquals(len(g1), 1)

        g1.remove( (self.tarek, self.likes, self.pizza) )

        # added graph is empty 
        self.assertEquals(len(g1), 0)

        # graph still exists, although empty
        self.assertEquals(set(x.identifier for x in self.graph.contexts()), 
                          set([self.c1, DATASET_DEFAULT_GRAPH_ID]))

        g.remove_graph(self.c1)
                
        # graph is gone
        self.assertEquals(set(x.identifier for x in self.graph.contexts()), 
                          set([DATASET_DEFAULT_GRAPH_ID]))
        
    def testDefaultGraph(self): 
        
        self.graph.add(( self.tarek, self.likes, self.pizza))
        self.assertEquals(len(self.graph), 1)
        # only default exists
        self.assertEquals(set(x.identifier for x in self.graph.contexts()), 
                          set([DATASET_DEFAULT_GRAPH_ID]))

        # removing default graph removes triples but not actual graph
        self.graph.remove_graph(DATASET_DEFAULT_GRAPH_ID)

        self.assertEquals(len(self.graph), 0)
        # default still exists
        self.assertEquals(set(x.identifier for x in self.graph.contexts()), 
                          set([DATASET_DEFAULT_GRAPH_ID]))

    def testNotUnion(self): 
        g1 = self.graph.graph(self.c1)
        g1.add((self.tarek, self.likes, self.pizza))

        self.assertEqual(list(self.graph.objects(self.tarek, None)), 
                         [])
        self.assertEqual(list(g1.objects(self.tarek, None)), [self.pizza])


# dynamically create classes for each registered Store

pluginname = None
if __name__ == '__main__':
    if len(sys.argv) > 1:
        pluginname = sys.argv[1]

tests = 0
for s in plugin.plugins(pluginname, plugin.Store):
    if s.name in ('default', 'IOMemory', 'Auditable',
                  'Concurrent', 'SPARQLStore', 'SPARQLUpdateStore'):
        continue  # these are tested by default
    if not s.getClass().graph_aware:
        continue

    locals()["t%d" % tests] = type("%sContextTestCase" % s.name, (
        DatasetTestCase,), {"store": s.name})
    tests += 1


if __name__ == '__main__':
    unittest.main()
