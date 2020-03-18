import unittest

from rdflib.graph import Graph
from rdflib.namespace import FOAF
from rdflib.term import URIRef
from six import b


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

        # should return empty qnames correctly
        self.assertEqual(g.compute_qname(URIRef("http://foo/bar/")),
            ("ns1", URIRef("http://foo/bar/"), ""))

    def test_reset(self):
        data = ('@prefix a: <http://example.org/a> .\n'
                'a: <http://example.org/b> <http://example.org/c> .')
        graph = Graph().parse(data=data, format='turtle')
        for p, n in tuple(graph.namespaces()):
            graph.store._IOMemory__namespace.pop(p)
            graph.store._IOMemory__prefix.pop(n)
        graph.namespace_manager.reset()
        self.assertFalse(tuple(graph.namespaces()))
        u = URIRef('http://example.org/a')
        prefix, namespace, name = graph.namespace_manager.compute_qname(u, generate=True)
        self.assertNotEqual(namespace, u)

    def test_reset_preserve_prefixes(self):
        data = ('@prefix a: <http://example.org/a> .\n'
                'a: <http://example.org/b> <http://example.org/c> .')
        graph = Graph().parse(data=data, format='turtle')
        graph.namespace_manager.reset()
        self.assertTrue(tuple(graph.namespaces()))
        u = URIRef('http://example.org/a')
        prefix, namespace, name = graph.namespace_manager.compute_qname(u, generate=True)
        self.assertEqual(namespace, u)

    def test_n3(self):
        g = Graph()
        g.add((URIRef("http://example.com/foo"),
               URIRef("http://example.com/bar"),
               URIRef("http://example.com/baz")))
        n3 = g.serialize(format="n3")
        # Gunnar disagrees that this is right:
        # self.assertTrue("<http://example.com/foo> ns1:bar <http://example.com/baz> ." in n3)
        # as this is much prettier, and ns1 is already defined:
        self.assertTrue(b("ns1:foo ns1:bar ns1:baz .") in n3)

    def test_n32(self):
        # this test not generating prefixes for subjects/objects
        g = Graph()
        g.add((URIRef("http://example1.com/foo"),
               URIRef("http://example2.com/bar"),
               URIRef("http://example3.com/baz")))
        n3 = g.serialize(format="n3")

        self.assertTrue(
            b("<http://example1.com/foo> ns1:bar <http://example3.com/baz> .") in n3)

    def test_closed_namespace(self):
        """Tests terms both in an out of the ClosedNamespace FOAF"""

        def add_not_in_namespace(s):
            return FOAF[s]

        # a blatantly non-existent FOAF property
        self.assertRaises(KeyError, add_not_in_namespace, "blah")

        # a deprecated FOAF property
        self.assertRaises(KeyError, add_not_in_namespace, "firstName")

        # a property name within the core FOAF namespace
        self.assertEqual(add_not_in_namespace("givenName"), URIRef("http://xmlns.com/foaf/0.1/givenName"))
