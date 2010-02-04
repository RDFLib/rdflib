"""
some more specific Literal tests are in test_literal.py
"""

import unittest

from rdflib.term import Literal, URIRef, BNode

class TestURIRefRepr(unittest.TestCase):
    """
    see also test_literal.TestRepr
    """
    
    def testSubclassNameAppearsInRepr(self):
        class MyURIRef(URIRef):
            pass
        x = MyURIRef('http://example.com/')
        self.assertEqual(repr(x), "MyURIRef('http://example.com/')")
        

class TestBNodeRepr(unittest.TestCase):
   
    def testSubclassNameAppearsInRepr(self):
        class MyBNode(BNode):
            pass
        x = MyBNode()
        self.assert_(repr(x).startswith("MyBNode("))
