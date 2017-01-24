"""
some more specific Literal tests are in test_literal.py
"""

import unittest
import base64

from rdflib.py3compat import format_doctest_out as uformat
from rdflib.term import URIRef, BNode, Literal, _is_valid_unicode
from rdflib.graph import QuotedGraph, Graph
from rdflib.namespace import XSD

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
        self.assertTrue(repr(x).startswith("MyBNode("))


class TestLiteral(unittest.TestCase):

    def test_base64_values(self):
        b64msg = 'cmRmbGliIGlzIGNvb2whIGFsc28gaGVyZSdzIHNvbWUgYmluYXJ5IAAR83UC'
        decoded_b64msg = base64.b64decode(b64msg)
        lit = Literal(b64msg, datatype=XSD.base64Binary)
        self.assertEqual(lit.value, decoded_b64msg)
        self.assertEqual(str(lit), b64msg)


class TestValidityFunctions(unittest.TestCase):

    def test_is_valid_unicode(self):
        testcase_list = (
            (None, True),
            (1, True),
            (['foo'], True),
            ({'foo': b'bar'}, True),
            ('foo', True),
            (b'foo\x00', True),
            (b'foo\xf3\x02', False)
        )
        for val, expected in testcase_list:
            self.assertEqual(_is_valid_unicode(val), expected)
