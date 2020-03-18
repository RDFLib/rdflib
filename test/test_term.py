"""
some more specific Literal tests are in test_literal.py
"""

import base64
import unittest
import random

from rdflib.term import URIRef, BNode, Literal, _is_valid_unicode
from rdflib.graph import QuotedGraph, Graph
from rdflib.namespace import XSD

from six import PY3


def uformat(s):
    if PY3:
        return s.replace("u'", "'")
    return s


class TestURIRefRepr(unittest.TestCase):
    """
    see also test_literal.TestRepr
    """

    def testSubclassNameAppearsInRepr(self):
        class MyURIRef(URIRef):
            pass
        x = MyURIRef('http://example.com/')
        self.assertEqual(repr(x), uformat("MyURIRef(u'http://example.com/')"))

    def testGracefulOrdering(self):
        u = URIRef('cake')
        g = Graph()
        a = u > u
        a = u > BNode()
        a = u > QuotedGraph(g.store, u)
        a = u > g


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

    def test_total_order(self):
        types = {
            XSD.dateTime: (
                '2001-01-01T00:00:00',
                '2001-01-01T00:00:00Z',
                '2001-01-01T00:00:00-00:00'
            ),
            XSD.date: (
                '2001-01-01',
                '2001-01-01Z',
                '2001-01-01-00:00'
            ),
            XSD.time: (
                '00:00:00',
                '00:00:00Z',
                '00:00:00-00:00'
            ),
            XSD.gYear: (
                '2001',
                '2001Z',
                '2001-00:00'
            ),  # interval
            XSD.gYearMonth: (
                '2001-01',
                '2001-01Z',
                '2001-01-00:00'
            ),
        }
        literals = [
            Literal(literal, datatype=t)
            for t, literals in types.items()
            for literal in literals
        ]
        try:
            sorted(literals)
            orderable = True
        except TypeError as e:
            for l in literals:
                print(repr(l), repr(l.value))
            print(e)
            orderable = False
        self.assertTrue(orderable)

        # also make sure that within a datetime things are still ordered:
        l1 = [
            Literal(l, datatype=XSD.dateTime)
            for l in [
                '2001-01-01T00:00:00',
                '2001-01-01T01:00:00',
                '2001-01-01T01:00:01',
                '2001-01-02T01:00:01',
                '2001-01-01T00:00:00Z',
                '2001-01-01T00:00:00-00:00',
                '2001-01-01T01:00:00Z',
                '2001-01-01T01:00:00-00:00',
                '2001-01-01T00:00:00-01:30',
                '2001-01-01T01:00:00-01:30',
                '2001-01-02T01:00:01Z',
                '2001-01-02T01:00:01-00:00',
                '2001-01-02T01:00:01-01:30'
            ]
        ]
        l2 = list(l1)
        random.shuffle(l2)
        self.assertListEqual(l1, sorted(l2))


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
