import unittest
import rdflib
import re

from rdflib.py3compat import b

class TestTrig(unittest.TestCase):

    def testEmpty(self):
        g=rdflib.Graph()
        s=g.serialize(format='trig')
        self.assertTrue(s is not None)

    def testRepeatTriples(self):
        g=rdflib.ConjunctiveGraph()
        g.get_context('urn:a').add(( rdflib.URIRef('urn:1'),
                                     rdflib.URIRef('urn:2'),
                                     rdflib.URIRef('urn:3') ))

        g.get_context('urn:b').add(( rdflib.URIRef('urn:1'),
                                     rdflib.URIRef('urn:2'),
                                     rdflib.URIRef('urn:3') ))

        self.assertEqual(len(g.get_context('urn:a')),1)
        self.assertEqual(len(g.get_context('urn:b')),1)

        s=g.serialize(format='trig')
        self.assert_(b('{}') not in s) # no empty graphs!

    def testSameSubject(self):
        g=rdflib.ConjunctiveGraph()
        g.get_context('urn:a').add(( rdflib.URIRef('urn:1'),
                                     rdflib.URIRef('urn:p1'),
                                     rdflib.URIRef('urn:o1') ))

        g.get_context('urn:b').add(( rdflib.URIRef('urn:1'),
                                     rdflib.URIRef('urn:p2'),
                                     rdflib.URIRef('urn:o2') ))

        self.assertEqual(len(g.get_context('urn:a')),1)
        self.assertEqual(len(g.get_context('urn:b')),1)

        s=g.serialize(format='trig')

        self.assertEqual(len(re.findall(b("p1"), s)), 1)
        self.assertEqual(len(re.findall(b("p2"), s)), 1)

        self.assert_(b('{}') not in s) # no empty graphs!
