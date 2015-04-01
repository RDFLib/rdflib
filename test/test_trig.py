import unittest
import rdflib
import re

from rdflib.py3compat import b

TRIPLE = (rdflib.URIRef("http://example.com/s"),
          rdflib.RDFS.label,
          rdflib.Literal("example 1"))

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

    def testRememberNamespace(self):
        g = rdflib.ConjunctiveGraph()
        g.add(TRIPLE + (rdflib.URIRef("http://example.com/graph1"),))
        # In 4.2.0 the first serialization would fail to include the
        # prefix for the graph but later serialize() calls would work.
        first_out = g.serialize(format='trig')
        second_out = g.serialize(format='trig')
        self.assert_(b'@prefix ns1: <http://example.com/> .' in second_out)
        self.assert_(b'@prefix ns1: <http://example.com/> .' in first_out)

    def testGraphQnameSyntax(self):
        g = rdflib.ConjunctiveGraph()
        g.add(TRIPLE + (rdflib.URIRef("http://example.com/graph1"),))
        out = g.serialize(format='trig')
        self.assert_(b'ns1:graph1 {' in out)

    def testGraphUriSyntax(self):
        g = rdflib.ConjunctiveGraph()
        # getQName will not abbreviate this, so it should serialize as
        # a '<...>' term.
        g.add(TRIPLE + (rdflib.URIRef("http://example.com/foo."),))
        out = g.serialize(format='trig')
        self.assert_(b'<http://example.com/foo.> {' in out)

    def testBlankGraphIdentifier(self):
        g = rdflib.ConjunctiveGraph()
        g.add(TRIPLE + (rdflib.BNode(),))
        out = g.serialize(format='trig')
        graph_label_line = out.splitlines()[-4]
        self.assert_(re.match(br'^_:[a-zA-Z0-9]+ \{', graph_label_line))
        
