"""
some more specific Literal tests are in test_literal.py
"""

import unittest
from rdflib.py3compat import format_doctest_out as uformat
from rdflib.term import URIRef, BNode
from rdflib.graph import QuotedGraph, Graph

class TestURIRefRepr(unittest.TestCase):
    """
    see also test_literal.TestRepr
    """
    
    def testSubclassNameAppearsInRepr(self):
        class MyURIRef(URIRef):
            pass
        x = MyURIRef('http://example.com/')
        self.assertEqual(repr(x), uformat("MyURIRef(%(u)s'http://example.com/')"))

    def testGracefulOrdering(self):
        u = URIRef('cake')
        g = Graph()
        a = u>u
        a = u>BNode()
        a = u>QuotedGraph(g.store, u)
        a = u>g
        
        
        
        

class TestBNodeRepr(unittest.TestCase):
   
    def testSubclassNameAppearsInRepr(self):
        class MyBNode(BNode):
            pass
        x = MyBNode()
        self.assert_(repr(x).startswith("MyBNode("))
