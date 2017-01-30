import sys
import os
import unittest

from tempfile import mkdtemp, mkstemp
import shutil
from rdflib import Graph, Dataset, URIRef, BNode, plugin
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID

from nose.exc import SkipTest


# Will also run SPARQLUpdateStore tests against local SPARQL1.1 endpoint if
# available. This assumes SPARQL1.1 query/update endpoints running locally at
# http://localhost:3030/db/
#
# Testing SPARQLUpdateStore Dataset behavior needs a different endpoint behavior
# than our ConjunctiveGraph tests in test_sparqlupdatestore.py!
#
# For the tests here to run, you can for example start fuseki with:
# ./fuseki-server --mem --update /db

# THIS WILL DELETE ALL DATA IN THE /db dataset

HOST = 'http://localhost:3030'
DB = '/db/'


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
        elif self.store == "SPARQLUpdateStore":
            root = HOST + DB
            self.graph.open((root + "sparql", root + "update"))
        else:
            self.tmppath = mkdtemp()

        if self.store != "SPARQLUpdateStore":
            self.graph.open(self.tmppath, create=True)
        self.michel = URIRef(u'urn:michel')
        self.tarek = URIRef(u'urn:tarek')
        self.bob = URIRef(u'urn:bob')
        self.likes = URIRef(u'urn:likes')
        self.hates = URIRef(u'urn:hates')
        self.pizza = URIRef(u'urn:pizza')
        self.cheese = URIRef(u'urn:cheese')

        # Use regular URIs because SPARQL endpoints like Fuseki alter short names
        self.c1 = URIRef(u'urn:context-1')
        self.c2 = URIRef(u'urn:context-2')

        # delete the graph for each test!
        self.graph.remove((None, None, None))
        for c in self.graph.contexts():
            c.remove((None, None, None))
            assert len(c) == 0
            self.graph.remove_graph(c)

    def tearDown(self):
        self.graph.close()
        if self.store == "SPARQLUpdateStore":
            pass
        else:
            if os.path.isdir(self.tmppath):
                shutil.rmtree(self.tmppath)
            else:
                os.remove(self.tmppath)


    def testGraphAware(self):

        if not self.graph.store.graph_aware: return

        g = self.graph
        g1 = g.graph(self.c1)

        # Some SPARQL endpoint backends (e.g. TDB) do not consider
        # empty named graphs
        if self.store != "SPARQLUpdateStore":
            # added graph exists
            self.assertEqual(set(x.identifier for x in self.graph.contexts()),
                              set([self.c1, DATASET_DEFAULT_GRAPH_ID]))

        # added graph is empty
        self.assertEqual(len(g1), 0)

        g1.add( (self.tarek, self.likes, self.pizza) )

        # added graph still exists
        self.assertEqual(set(x.identifier for x in self.graph.contexts()),
                          set([self.c1, DATASET_DEFAULT_GRAPH_ID]))

        # added graph contains one triple
        self.assertEqual(len(g1), 1)

        g1.remove( (self.tarek, self.likes, self.pizza) )

        # added graph is empty
        self.assertEqual(len(g1), 0)

        # Some SPARQL endpoint backends (e.g. TDB) do not consider
        # empty named graphs
        if self.store != "SPARQLUpdateStore":
            # graph still exists, although empty
            self.assertEqual(set(x.identifier for x in self.graph.contexts()),
                              set([self.c1, DATASET_DEFAULT_GRAPH_ID]))

        g.remove_graph(self.c1)

        # graph is gone
        self.assertEqual(set(x.identifier for x in self.graph.contexts()),
                          set([DATASET_DEFAULT_GRAPH_ID]))

    def testDefaultGraph(self):
        # Something the default graph is read-only (e.g. TDB in union mode)
        if self.store == "SPARQLUpdateStore":
            print("Please make sure updating the default graph " \
                  "is supported by your SPARQL endpoint")

        self.graph.add(( self.tarek, self.likes, self.pizza))
        self.assertEqual(len(self.graph), 1)
        # only default exists
        self.assertEqual(set(x.identifier for x in self.graph.contexts()),
                          set([DATASET_DEFAULT_GRAPH_ID]))

        # removing default graph removes triples but not actual graph
        self.graph.remove_graph(DATASET_DEFAULT_GRAPH_ID)

        self.assertEqual(len(self.graph), 0)
        # default still exists
        self.assertEqual(set(x.identifier for x in self.graph.contexts()),
                          set([DATASET_DEFAULT_GRAPH_ID]))

    def testNotUnion(self):
        # Union depends on the SPARQL endpoint configuration
        if self.store == "SPARQLUpdateStore":
            print("Please make sure your SPARQL endpoint has not configured " \
                  "its default graph as the union of the named graphs")
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
                  'Concurrent', 'SPARQLStore'):
        continue  # these are tested by default

    if not s.getClass().graph_aware:
        continue

    if s.name == "SPARQLUpdateStore":
        from six.moves.urllib.request import urlopen
        try:
            assert len(urlopen(HOST).read()) > 0
        except:
            sys.stderr.write("No SPARQL endpoint for %s (tests skipped)\n" % s.name)
            continue

    locals()["t%d" % tests] = type("%sContextTestCase" % s.name, (
        DatasetTestCase,), {"store": s.name})
    tests += 1


if __name__ == '__main__':
    unittest.main()
