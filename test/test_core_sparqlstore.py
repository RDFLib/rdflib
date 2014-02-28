import unittest
try:
    import SPARQLWrapper
except ImportError:
    from nose.exc import SkipTest
    raise SkipTest("SPARQLWrapper not installed")

from rdflib.graph import Graph


class TestSPARQLStoreGraphCore(unittest.TestCase):

    store_name = 'SPARQLStore'
    path = "http://dbpedia.org/sparql"
    storetest = True
    create = False

    def setUp(self):
        self.graph = Graph(store="SPARQLStore")
        self.graph.open(self.path, create=self.create)
        ns = list(self.graph.namespaces())
        assert len(ns) > 0, ns

    def tearDown(self):
        self.graph.close()

    def test(self):
        print("Done")

if __name__ == '__main__':
    unittest.main()
