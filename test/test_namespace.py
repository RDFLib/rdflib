import unittest
from unittest.case import expectedFailure

from warnings import warn

from rdflib import DCTERMS
from rdflib.graph import Graph
from rdflib.namespace import (
    FOAF,
    OWL,
    RDF,
    RDFS,
    SH,
    DefinedNamespaceMeta,
    Namespace,
    ClosedNamespace,
    URIPattern,
)
from rdflib.term import URIRef


class NamespaceTest(unittest.TestCase):
    def setUp(self):
        self.ns_str = "http://example.com/name/space/"
        self.ns = Namespace(self.ns_str)

    def test_repr(self):
        # NOTE: this assumes ns_str has no characthers that need escaping
        self.assertIn(self.ns_str, f"{self.ns!r}")
        self.assertEqual(self.ns, eval(f"{self.ns!r}"))

    def test_str(self):
        self.assertEqual(self.ns_str, f"{self.ns}")

    def test_member(self):
        self.assertEqual(f"{self.ns_str}a", f"{self.ns.a}")

    def test_dcterms_title(self):
        self.assertEqual(DCTERMS.title, URIRef(DCTERMS + "title"))

    def test_iri(self):
        prefix = "http://jörn.loves.encoding.problems/"
        ns = Namespace(prefix)
        self.assertEqual(ns, str(prefix))
        self.assert_(ns["jörn"].startswith(ns))


class ClosedNamespaceTest(unittest.TestCase):
    def setUp(self):
        self.ns_str = "http://example.com/name/space/"
        self.ns = ClosedNamespace(self.ns_str, ["a", "b", "c"])

    def test_repr(self):
        # NOTE: this assumes ns_str has no characthers that need escaping
        self.assertIn(self.ns_str, f"{self.ns!r}")

    @expectedFailure
    def test_repr_ef(self):
        """
        This fails because ClosedNamespace repr does not represent the second argument
        """
        self.assertEqual(self.ns, eval(f"{self.ns!r}"))

    def test_str(self):
        self.assertEqual(self.ns_str, f"{self.ns}")

    def test_member(self):
        self.assertEqual(f"{self.ns_str}a", f"{self.ns.a}")

    def test_missing_member(self):
        with self.assertRaises(AttributeError) as context:
            f"{self.ns.missing}"
        self.assertIn("missing", f"{context.exception}")


class URIPatternTest(unittest.TestCase):
    def setUp(self):
        self.pattern_str = "http://example.org/%s/%d/resource"
        self.pattern = URIPattern(self.pattern_str)

    def test_repr(self):
        # NOTE: this assumes pattern_str has no characthers that need escaping
        self.assertIn(self.pattern_str, f"{self.pattern!r}")
        self.assertEqual(self.pattern, eval(f"{self.pattern!r}"))

    def test_format(self):
        self.assertEqual(
            "http://example.org/foo/100/resource", str(self.pattern % ("foo", 100))
        )


class NamespacePrefixTest(unittest.TestCase):
    def test_compute_qname(self):
        """Test sequential assignment of unknown prefixes"""
        g = Graph()
        self.assertEqual(
            g.compute_qname(URIRef("http://foo/bar/baz")),
            ("ns1", URIRef("http://foo/bar/"), "baz"),
        )

        self.assertEqual(
            g.compute_qname(URIRef("http://foo/bar#baz")),
            ("ns2", URIRef("http://foo/bar#"), "baz"),
        )

        # should skip to ns4 when ns3 is already assigned
        g.bind("ns3", URIRef("http://example.org/"))
        self.assertEqual(
            g.compute_qname(URIRef("http://blip/blop")),
            ("ns4", URIRef("http://blip/"), "blop"),
        )

        # should return empty qnames correctly
        self.assertEqual(
            g.compute_qname(URIRef("http://foo/bar/")),
            ("ns1", URIRef("http://foo/bar/"), ""),
        )

        # should compute qnames of URNs correctly as well
        self.assertEqual(
            g.compute_qname(URIRef("urn:ISSN:0167-6423")),
            ("ns5", URIRef("urn:ISSN:"), "0167-6423"),
        )

        self.assertEqual(
            g.compute_qname(URIRef("urn:ISSN:")),
            ("ns5", URIRef("urn:ISSN:"), ""),
        )

        # should compute qnames with parenthesis correctly
        self.assertEqual(
            g.compute_qname(URIRef("http://foo/bar/name_with_(parenthesis)")),
            ("ns1", URIRef("http://foo/bar/"), "name_with_(parenthesis)"),
        )

    def test_reset(self):
        data = (
            "@prefix a: <http://example.org/a> .\n"
            "a: <http://example.org/b> <http://example.org/c> ."
        )
        graph = Graph().parse(data=data, format="turtle")
        for p, n in tuple(graph.namespaces()):
            graph.store._Memory__namespace.pop(p)
            graph.store._Memory__prefix.pop(n)
        graph.namespace_manager.reset()
        self.assertFalse(tuple(graph.namespaces()))
        u = URIRef("http://example.org/a")
        prefix, namespace, name = graph.namespace_manager.compute_qname(
            u, generate=True
        )
        self.assertNotEqual(namespace, u)

    def test_reset_preserve_prefixes(self):
        data = (
            "@prefix a: <http://example.org/a> .\n"
            "a: <http://example.org/b> <http://example.org/c> ."
        )
        graph = Graph().parse(data=data, format="turtle")
        graph.namespace_manager.reset()
        self.assertTrue(tuple(graph.namespaces()))
        u = URIRef("http://example.org/a")
        prefix, namespace, name = graph.namespace_manager.compute_qname(
            u, generate=True
        )
        self.assertEqual(namespace, u)

    def test_n3(self):
        g = Graph()
        g.add(
            (
                URIRef("http://example.com/foo"),
                URIRef("http://example.com/bar"),
                URIRef("http://example.com/baz"),
            )
        )
        n3 = g.serialize(format="n3", encoding="latin-1")
        # Gunnar disagrees that this is right:
        # self.assertTrue("<http://example.com/foo> ns1:bar <http://example.com/baz> ." in n3)
        # as this is much prettier, and ns1 is already defined:
        self.assertTrue(b"ns1:foo ns1:bar ns1:baz ." in n3)

    def test_n32(self):
        # this test not generating prefixes for subjects/objects
        g = Graph()
        g.add(
            (
                URIRef("http://example1.com/foo"),
                URIRef("http://example2.com/bar"),
                URIRef("http://example3.com/baz"),
            )
        )
        n3 = g.serialize(format="n3", encoding="latin-1")

        self.assertTrue(
            b"<http://example1.com/foo> ns1:bar <http://example3.com/baz> ." in n3
        )

    def test_closed_namespace(self):
        """Tests terms both in an out of the ClosedNamespace FOAF"""

        def add_not_in_namespace(s):
            with self.assertRaises(AttributeError):
                return FOAF[s]

        # a non-existent FOAF property
        add_not_in_namespace("blah")

        # a deprecated FOAF property
        # add_not_in_namespace('firstName')
        self.assertEqual(
            FOAF["firstName"],
            URIRef("http://xmlns.com/foaf/0.1/firstName"),
        )
        warn("DefinedNamespace does not address deprecated properties")

        # a property name within the FOAF namespace
        self.assertEqual(
            FOAF.givenName,
            URIRef("http://xmlns.com/foaf/0.1/givenName"),
        )

        # namescape can be used as str
        self.assertTrue(FOAF.givenName.startswith(FOAF))

    def test_contains_method(self):
        """Tests for Namespace.__contains__() methods."""

        ref = URIRef("http://www.w3.org/ns/shacl#Info")
        self.assertTrue(
            type(SH) == DefinedNamespaceMeta,
            f"SH no longer a DefinedNamespaceMeta (instead it is now {type(SH)}, update test.",
        )
        self.assertTrue(ref in SH, "sh:Info not in SH")

        ref = URIRef("http://www.w3.org/2000/01/rdf-schema#label")
        self.assertTrue(
            ref in RDFS, "ClosedNamespace(RDFS) does not include rdfs:label"
        )
        ref = URIRef("http://www.w3.org/2000/01/rdf-schema#example")
        self.assertFalse(
            ref in RDFS, "ClosedNamespace(RDFS) includes out-of-ns member rdfs:example"
        )

        ref = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
        self.assertTrue(ref in RDF, "RDF does not include rdf:type")

        ref = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#_1")
        self.assertTrue(ref in RDF, "RDF does not include rdf:_1")

        ref = URIRef("http://www.w3.org/2002/07/owl#rational")
        self.assertTrue(ref in OWL, "OWL does not include owl:rational")

        ref = URIRef("http://www.w3.org/2002/07/owl#real")
        self.assertTrue(ref in OWL, "OWL does not include owl:real")
