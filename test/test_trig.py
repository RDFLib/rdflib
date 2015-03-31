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

        self.assertTrue('None' not in data)
