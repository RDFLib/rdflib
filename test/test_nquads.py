import os
import unittest
from rdflib import Dataset, URIRef, Namespace
from test import TEST_DIR

TEST_BASE = "test/nquads.rdflib"


class NQuadsParserTest(unittest.TestCase):
    def _load_example(self, default_union=False):
        ds = Dataset(default_union=default_union)
        nq_path = os.path.relpath(
            os.path.join(TEST_DIR, "nquads.rdflib/example.nquads"), os.curdir
        )
        with open(nq_path, "rb") as data:
            ds.parse(data, format="nquads")
        return ds

    def test_01_simple_open(self):
        ds = self._load_example()
        assert len(ds.store) == 449

    def test_02_contexts(self):
        # There should be 16 separate contexts
        ds = self._load_example()
        assert len([x for x in ds.store.contexts()]) == 16
        assert len(list(ds.contexts())) == 16

    def test_03_get_value(self):
        # is the name of entity E10009 "Arco Publications"?
        # (in graph http://bibliographica.org/entity/E10009)
        # Looking for:
        # <http://bibliographica.org/entity/E10009>
        #       <http://xmlns.com/foaf/0.1/name>
        #       "Arco Publications"
        #       <http://bibliographica.org/entity/E10009>

        ds = self._load_example(default_union=True)
        s = URIRef("http://bibliographica.org/entity/E10009")
        FOAF = Namespace("http://xmlns.com/foaf/0.1/")
        self.assertTrue(ds.value(s, FOAF.name).eq("Arco Publications"))

    def test_context_is_optional(self):
        ds = Dataset()
        nq_path = os.path.relpath(
            os.path.join(TEST_DIR, "nquads.rdflib/test6.nq"), os.curdir
        )
        with open(nq_path, "rb") as data:
            ds.parse(data, format="nquads")
        assert len(ds) > 0

    def test_serialize(self):
        ds1 = Dataset()
        uri1 = URIRef("http://example.org/mygraph1")
        uri2 = URIRef("http://example.org/mygraph2")

        bob = URIRef("urn:example:bob")
        likes = URIRef("urn:example:likes")
        pizza = URIRef("urn:example:pizza")

        ds1.graph(uri1).add((bob, likes, pizza))
        ds1.graph(uri2).add((bob, likes, pizza))

        s = ds1.serialize(format="nquads", encoding="utf-8")
        self.assertEqual(len([x for x in s.split(b"\n") if x.strip()]), 2)

        ds2 = Dataset()
        ds2.parse(data=s, format="nquads")

        self.assertEqual(len(ds1), len(ds2))
        self.assertEqual(
            sorted(list(ds1.contexts())),
            sorted(list(ds2.contexts())),
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
        ds1 = Dataset()
        ds2 = Dataset()
        ds1.parse(self.data, format="nquads", bnode_context=bnode_ctx)
        self.data.seek(0)
        ds2.parse(self.data, format="nquads", bnode_context=bnode_ctx)
        self.assertEqual(set(ds2.subjects()), set(ds1.subjects()))

    def test_parse_shared_bnode_context_same_graph(self):
        bnode_ctx = dict()
        ds = Dataset()
        ds.parse(self.data_obnodes, format="nquads", bnode_context=bnode_ctx)
        o1 = set(ds.objects())
        self.data_obnodes.seek(0)
        ds.parse(self.data_obnodes, format="nquads", bnode_context=bnode_ctx)
        o2 = set(ds.objects())
        self.assertEqual(o1, o2)

    def test_parse_distinct_bnode_context(self):
        ds = Dataset(default_union=True)
        ds.parse(self.data, format="nquads", bnode_context=dict())
        s1 = set(ds.subjects())
        self.data.seek(0)
        ds.parse(self.data, format="nquads", bnode_context=dict())
        s2 = set(ds.subjects())
        assert s2 != set()
        self.assertNotEqual(set(), s2 - s1)

    def test_parse_distinct_bnode_contexts_between_graphs(self):
        ds1 = Dataset(default_union=True)
        ds2 = Dataset(default_union=True)
        ds1.parse(self.data, format="nquads")
        s1 = set(ds1.subjects())
        self.data.seek(0)
        ds2.parse(self.data, format="nquads")
        s2 = set(ds2.subjects())
        assert s2 != set()
        self.assertNotEqual(s1, s2)

    def test_parse_distinct_bnode_contexts_named_graphs(self):
        ds1 = Dataset()
        ds2 = Dataset()
        ds1.parse(self.data, format="nquads")
        self.data.seek(0)
        ds2.parse(self.data, format="nquads")
        self.assertNotEqual(set(ds2.contexts()), set(ds1.contexts()))

    def test_parse_shared_bnode_contexts_named_graphs(self):
        bnode_ctx = dict()
        ds1 = Dataset()
        ds2 = Dataset()
        ds1.parse(self.data, format="nquads", bnode_context=bnode_ctx)
        self.data.seek(0)
        ds2.parse(self.data, format="nquads", bnode_context=bnode_ctx)
        self.assertEqual(set(ds2.contexts()), set(ds1.contexts()))


if __name__ == "__main__":
    unittest.main()
