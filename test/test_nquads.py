import os
import unittest
from rdflib import ConjunctiveGraph, URIRef, Namespace
from test import TEST_DIR

TEST_BASE = "test/nquads.rdflib"


class NQuadsParserTest(unittest.TestCase):
    def _load_example(self):
        g = ConjunctiveGraph()
        nq_path = os.path.relpath(
            os.path.join(TEST_DIR, "nquads.rdflib/example.nquads"), os.curdir
        )
        with open(nq_path, "rb") as data:
            g.parse(data, format="nquads")
        return g

    def test_01_simple_open(self):
        g = self._load_example()
        assert len(g.store) == 449

    def test_02_contexts(self):
        # There should be 16 separate contexts
        g = self._load_example()
        assert len([x for x in g.store.contexts()]) == 16

    def test_03_get_value(self):
        # is the name of entity E10009 "Arco Publications"?
        # (in graph http://bibliographica.org/entity/E10009)
        # Looking for:
        # <http://bibliographica.org/entity/E10009>
        #       <http://xmlns.com/foaf/0.1/name>
        #       "Arco Publications"
        #       <http://bibliographica.org/entity/E10009>

        g = self._load_example()
        s = URIRef("http://bibliographica.org/entity/E10009")
        FOAF = Namespace("http://xmlns.com/foaf/0.1/")
        self.assertTrue(g.value(s, FOAF.name).eq("Arco Publications"))

    def test_context_is_optional(self):
        g = ConjunctiveGraph()
        nq_path = os.path.relpath(
            os.path.join(TEST_DIR, "nquads.rdflib/test6.nq"), os.curdir
        )
        with open(nq_path, "rb") as data:
            g.parse(data, format="nquads")
        assert len(g) > 0

    def test_serialize(self):
        g = ConjunctiveGraph()
        uri1 = URIRef("http://example.org/mygraph1")
        uri2 = URIRef("http://example.org/mygraph2")

        bob = URIRef("urn:bob")
        likes = URIRef("urn:likes")
        pizza = URIRef("urn:pizza")

        g.get_context(uri1).add((bob, likes, pizza))
        g.get_context(uri2).add((bob, likes, pizza))

        s = g.serialize(format="nquads", encoding="latin-1")
        self.assertEqual(len([x for x in s.split(b"\n") if x.strip()]), 2)

        g2 = ConjunctiveGraph()
        g2.parse(data=s, format="nquads")

        self.assertEqual(len(g), len(g2))
        self.assertEqual(
            sorted(x.identifier for x in g.contexts()),
            sorted(x.identifier for x in g2.contexts()),
        )


class BnodeContextTest(unittest.TestCase):
    def setUp(self):
        self.data = open("test/nquads.rdflib/bnode_context.nquads", "rb")
        self.data_obnodes = open(
            "test/nquads.rdflib/bnode_context_obj_bnodes.nquads", "rb"
        )

    def tearDown(self):
        self.data.close()

    def test_parse_shared_bnode_context(self):
        bnode_ctx = dict()
        g = ConjunctiveGraph()
        h = ConjunctiveGraph()
        g.parse(self.data, format="nquads", bnode_context=bnode_ctx)
        self.data.seek(0)
        h.parse(self.data, format="nquads", bnode_context=bnode_ctx)
        self.assertEqual(set(h.subjects()), set(g.subjects()))

    def test_parse_shared_bnode_context_same_graph(self):
        bnode_ctx = dict()
        g = ConjunctiveGraph()
        g.parse(self.data_obnodes, format="nquads", bnode_context=bnode_ctx)
        o1 = set(g.objects())
        self.data_obnodes.seek(0)
        g.parse(self.data_obnodes, format="nquads", bnode_context=bnode_ctx)
        o2 = set(g.objects())
        self.assertEqual(o1, o2)

    def test_parse_distinct_bnode_context(self):
        g = ConjunctiveGraph()
        g.parse(self.data, format="nquads", bnode_context=dict())
        s1 = set(g.subjects())
        self.data.seek(0)
        g.parse(self.data, format="nquads", bnode_context=dict())
        s2 = set(g.subjects())
        self.assertNotEqual(set(), s2 - s1)

    def test_parse_distinct_bnode_contexts_between_graphs(self):
        g = ConjunctiveGraph()
        h = ConjunctiveGraph()
        g.parse(self.data, format="nquads")
        s1 = set(g.subjects())
        self.data.seek(0)
        h.parse(self.data, format="nquads")
        s2 = set(h.subjects())
        self.assertNotEqual(s1, s2)

    def test_parse_distinct_bnode_contexts_named_graphs(self):
        g = ConjunctiveGraph()
        h = ConjunctiveGraph()
        g.parse(self.data, format="nquads")
        self.data.seek(0)
        h.parse(self.data, format="nquads")
        self.assertNotEqual(set(h.contexts()), set(g.contexts()))

    def test_parse_shared_bnode_contexts_named_graphs(self):
        bnode_ctx = dict()
        g = ConjunctiveGraph()
        h = ConjunctiveGraph()
        g.parse(self.data, format="nquads", bnode_context=bnode_ctx)
        self.data.seek(0)
        h.parse(self.data, format="nquads", bnode_context=bnode_ctx)
        self.assertEqual(set(h.contexts()), set(g.contexts()))


if __name__ == "__main__":
    unittest.main()
