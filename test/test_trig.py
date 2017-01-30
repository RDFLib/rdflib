import unittest
import rdflib
import re

from nose import SkipTest
from six import b

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
        self.assertTrue(b('{}') not in s) # no empty graphs!

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

        self.assertTrue(b('{}') not in s) # no empty graphs!

    def testRememberNamespace(self):
        g = rdflib.ConjunctiveGraph()
        g.add(TRIPLE + (rdflib.URIRef("http://example.com/graph1"),))
        # In 4.2.0 the first serialization would fail to include the
        # prefix for the graph but later serialize() calls would work.
        first_out = g.serialize(format='trig')
        second_out = g.serialize(format='trig')
        self.assertTrue(b'@prefix ns1: <http://example.com/> .' in second_out)
        self.assertTrue(b'@prefix ns1: <http://example.com/> .' in first_out)

    def testGraphQnameSyntax(self):
        g = rdflib.ConjunctiveGraph()
        g.add(TRIPLE + (rdflib.URIRef("http://example.com/graph1"),))
        out = g.serialize(format='trig')
        self.assertTrue(b'ns1:graph1 {' in out)

    def testGraphUriSyntax(self):
        g = rdflib.ConjunctiveGraph()
        # getQName will not abbreviate this, so it should serialize as
        # a '<...>' term.
        g.add(TRIPLE + (rdflib.URIRef("http://example.com/foo."),))
        out = g.serialize(format='trig')
        self.assertTrue(b'<http://example.com/foo.> {' in out)

    def testBlankGraphIdentifier(self):
        g = rdflib.ConjunctiveGraph()
        g.add(TRIPLE + (rdflib.BNode(),))
        out = g.serialize(format='trig')
        graph_label_line = out.splitlines()[-4]

        self.assertTrue(re.match(br'^_:[a-zA-Z0-9]+ \{', graph_label_line))

    def testGraphParsing(self):
        # should parse into single default graph context
        data = """
<http://example.com/thing#thing_a> <http://example.com/knows> <http://example.com/thing#thing_b> .
"""
        g = rdflib.ConjunctiveGraph()
        g.parse(data=data, format='trig')
        self.assertEqual(len(list(g.contexts())), 1)

        # should parse into single default graph context
        data = """
<http://example.com/thing#thing_a> <http://example.com/knows> <http://example.com/thing#thing_b> .

{ <http://example.com/thing#thing_c> <http://example.com/knows> <http://example.com/thing#thing_d> . }
"""
        g = rdflib.ConjunctiveGraph()
        g.parse(data=data, format='trig')
        self.assertEqual(len(list(g.contexts())), 1)

        # should parse into 2 contexts, one default, one named
        data = """
<http://example.com/thing#thing_a> <http://example.com/knows> <http://example.com/thing#thing_b> .

{ <http://example.com/thing#thing_c> <http://example.com/knows> <http://example.com/thing#thing_d> . }

<http://example.com/graph#graph_a> {
    <http://example.com/thing/thing_e> <http://example.com/knows> <http://example.com/thing#thing_f> .
}
"""
        g = rdflib.ConjunctiveGraph()
        g.parse(data=data, format='trig')
        self.assertEqual(len(list(g.contexts())), 2)

    def testRoundTrips(self):

        raise SkipTest('skipped until 5.0')

        data = """
<http://example.com/thing#thing_a> <http://example.com/knows> <http://example.com/thing#thing_b> .

{ <http://example.com/thing#thing_c> <http://example.com/knows> <http://example.com/thing#thing_d> . }

<http://example.com/graph#graph_a> {
    <http://example.com/thing/thing_e> <http://example.com/knows> <http://example.com/thing#thing_f> .
}
"""
        g = rdflib.ConjunctiveGraph()
        for i in range(5):
            g.parse(data=data, format='trig')
            data = g.serialize(format='trig')

        # output should only contain 1 mention of each resource/graph name
        self.assertEqual(data.count('thing_a'), 1)
        self.assertEqual(data.count('thing_b'), 1)
        self.assertEqual(data.count('thing_c'), 1)
        self.assertEqual(data.count('thing_d'), 1)
        self.assertEqual(data.count('thing_e'), 1)
        self.assertEqual(data.count('thing_f'), 1)
        self.assertEqual(data.count('graph_a'), 1)

    def testDefaultGraphSerializesWithoutName(self):
        data = """
<http://example.com/thing#thing_a> <http://example.com/knows> <http://example.com/thing#thing_b> .

{ <http://example.com/thing#thing_c> <http://example.com/knows> <http://example.com/thing#thing_d> . }
"""
        g = rdflib.ConjunctiveGraph()
        g.parse(data=data, format='trig')
        data = g.serialize(format='trig')

        self.assertTrue(b('None') not in data)

    def testPrefixes(self):

        data = """
        @prefix ns1: <http://ex.org/schema#> .
        <http://ex.org/docs/document1> = {
            ns1:Person_A a ns1:Person ;
                ns1:TextSpan "Simon" .
        }
        <http://ex.org/docs/document2> = {
            ns1:Person_C a ns1:Person ;
                ns1:TextSpan "Agnes" .
        }
        """

        cg = rdflib.ConjunctiveGraph()
        cg.parse(data=data, format='trig')
        data = cg.serialize(format='trig')

        self.assert_(b('ns2: <http://ex.org/docs/') in data, data)
        self.assert_(b('<ns2:document1>') not in data, data)
        self.assert_(b('ns2:document1') in data, data)
