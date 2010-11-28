import unittest

from rdflib.graph import Graph
from rdflib.term import URIRef

class NamespacePrefixTest(unittest.TestCase):

    def test_compute_qname(self):
        """Test sequential assignment of unknown prefixes"""
        g = Graph()
        self.assertEqual(g.compute_qname(URIRef("http://foo/bar/baz")),
            ("ns1", URIRef("http://foo/bar/"), "baz"))

        self.assertEqual(g.compute_qname(URIRef("http://foo/bar#baz")),
            ("ns2", URIRef("http://foo/bar#"), "baz"))
        
        # should skip to ns4 when ns3 is already assigned
        g.bind("ns3", URIRef("http://example.org/"))
        self.assertEqual(g.compute_qname(URIRef("http://blip/blop")),
            ("ns4", URIRef("http://blip/"), "blop"))

    def test_n3(self):
        g = Graph()
        g.add((URIRef("http://example.com/foo"),
               URIRef("http://example.com/bar"),
               URIRef("http://example.com/baz")))
        n3 = g.serialize(format="n3")
        self.assertTrue("<http://example.com/foo> ns1:bar <http://example.com/baz> ." in n3)
