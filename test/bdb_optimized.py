import unittest
from rdflib.graph import ConjunctiveGraph
from context import ContextTestCase
from graph import GraphTestCase
from tempfile import mkdtemp

class TestBDBGraph(GraphTestCase):
    store_name = "BDBOptimized"

class TestBDBContext(ContextTestCase):
    store = "BDBOptimized"

class TestBDBOptimized:
    def setUp(self):
        self.graph = ConjunctiveGraph(store="BDBOptimized")
        self.path = mkdtemp()
        self.graph.open(self.path, create=True)
                    
    def tearDown(self):
        self.graph.close()

if __name__ == "__main__":
    bdb_suite = unittest.TestSuite()

    context_suite = unittest.TestSuite()    
    context_suite.addTest(TestBDBContext('testAdd'))
    context_suite.addTest(TestBDBContext('testRemove'))
    context_suite.addTest(TestBDBContext('testLenInOneContext'))
    context_suite.addTest(TestBDBContext('testLenInMultipleContexts'))
    context_suite.addTest(TestBDBContext('testConjunction'))
    context_suite.addTest(TestBDBContext('testRemoveInMultipleContexts'))
    context_suite.addTest(TestBDBContext('testContexts'))
    context_suite.addTest(TestBDBContext('testRemoveContext'))
    context_suite.addTest(TestBDBContext('testRemoveAny'))
    context_suite.addTest(TestBDBContext('testTriples'))

    graph_suite = unittest.TestSuite()
    graph_suite.addTest(TestBDBGraph('testAdd'))
    graph_suite.addTest(TestBDBGraph('testRemove'))
    graph_suite.addTest(TestBDBGraph('testTriples'))
    graph_suite.addTest(TestBDBGraph('testStatementNode'))
    graph_suite.addTest(TestBDBGraph('testGraphValue'))
    graph_suite.addTest(TestBDBGraph('testConnected'))
        
    unittest.TextTestRunner(verbosity=2).run(graph_suite)
    unittest.TextTestRunner(verbosity=2).run(context_suite)
    
#    unittest.main()    
