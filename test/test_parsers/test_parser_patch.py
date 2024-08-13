import os

import pytest

from rdflib import BNode, Dataset, URIRef
from test.data import TEST_DATA_DIR

TEST_BASE = os.path.join(TEST_DATA_DIR, "patch")


class TestPatchParser:
    def test_01(self):
        ds = Dataset()
        nq_path = os.path.relpath(
            os.path.join(TEST_DATA_DIR, "patch/add_triple_and_quad.rdp"), os.curdir
        )
        with open(nq_path, "rb") as data:
            ds.parse(data, format="patch")
        assert len(ds) == 2

    def test_02(self):
        ds = Dataset()
        nq_path = os.path.relpath(
            os.path.join(TEST_DATA_DIR, "patch/add_and_delete_bnode_triples.rdp"),
            os.curdir,
        )
        with open(nq_path, "rb") as data:
            ds.parse(data, format="patch")
        assert len(ds) == 2

    def test_03(self):
        ds = Dataset()
        nq_path = os.path.relpath(
            os.path.join(TEST_DATA_DIR, "patch/add_and_delete_triples.rdp"), os.curdir
        )
        with open(nq_path, "rb") as data:
            ds.parse(data, format="patch")
        assert len(ds) == 0

    def test_04(self):
        ds = Dataset()
        nq_path = os.path.relpath(
            os.path.join(TEST_DATA_DIR, "patch/add_prefix.rdp"), os.curdir
        )
        with open(nq_path, "rb") as data:
            ds.parse(data, format="patch")
        namespaces = [tup[0] for tup in (ds.namespaces())]
        assert "testing" in namespaces

    def test_05(self):
        ds = Dataset()
        nq_path = os.path.relpath(
            os.path.join(TEST_DATA_DIR, "patch/add_and_delete_prefix.rdp"), os.curdir
        )
        with open(nq_path, "rb") as data:
            ds.parse(data, format="patch")
        namespaces = [tup[0] for tup in (ds.namespaces())]
        assert "present" in namespaces
        assert (
            "@prefix removed: <http://ns-for-prefix-to-remove#> ." not in ds.serialize()
        )

    def test_06(self):
        ds = Dataset()
        add_bnode_triple_path = os.path.relpath(
            os.path.join(TEST_DATA_DIR, "patch/add_bnode_triple.rdp"), os.curdir
        )
        with open(add_bnode_triple_path, "rb") as data:
            ds.parse(data, format="patch")
        assert len(ds) == 1
        delete_bnode_triple_path = os.path.relpath(
            os.path.join(TEST_DATA_DIR, "patch/delete_bnode_triple.rdp"), os.curdir
        )
        with open(delete_bnode_triple_path, "rb") as data:
            ds.parse(data, format="patch")
        assert len(ds) == 0

    @pytest.mark.xfail(reason="De skolemization is undone by ConjunctiveGraph")
    def test_07(self):
        ds = Dataset()
        add_bnode_triple_path = os.path.relpath(
            os.path.join(TEST_DATA_DIR, "patch/add_bnode_triple.rdp"), os.curdir
        )
        with open(add_bnode_triple_path, "rb") as data:
            ds.parse(data, format="patch")
        # test will pass if changed to `for t in ds.de_skolemize():`:
        for t in ds:
            assert BNode("bn1") in t
            assert (
                URIRef("https://rdflib.github.io/.well-known/genid/rdflib/bn1") not in t
            )

    def test_08(self):
        ds = Dataset()
        add_bnode_quad_path = os.path.relpath(
            os.path.join(TEST_DATA_DIR, "patch/add_bnode_quad.rdp"), os.curdir
        )
        with open(add_bnode_quad_path, "rb") as data:
            ds.parse(data, format="patch")
        assert len(ds) == 1
        delete_bnode_quad_path = os.path.relpath(
            os.path.join(TEST_DATA_DIR, "patch/delete_bnode_quad.rdp"), os.curdir
        )
        with open(delete_bnode_quad_path, "rb") as data:
            ds.parse(data, format="patch")
        assert len(ds) == 0

    def test_09(self):
        ds = Dataset()
        add_bnode_graph_path = os.path.relpath(
            os.path.join(TEST_DATA_DIR, "patch/add_bnode_graph.rdp"), os.curdir
        )
        with open(add_bnode_graph_path, "rb") as data:
            ds.parse(data, format="patch")
        assert len(ds) == 1
        delete_bnode_graph_path = os.path.relpath(
            os.path.join(TEST_DATA_DIR, "patch/delete_bnode_graph.rdp"), os.curdir
        )
        with open(delete_bnode_graph_path, "rb") as data:
            ds.parse(data, format="patch")
        assert len(ds) == 0

    def test_10(self):
        ds = Dataset()
        add_bnode_uri_path = os.path.relpath(
            os.path.join(TEST_DATA_DIR, "patch/add_bnode_uri.rdp"), os.curdir
        )
        with open(add_bnode_uri_path, "rb") as data:
            ds.parse(data, format="patch")
        assert len(ds) == 1
        delete_bnode_uri_path = os.path.relpath(
            os.path.join(TEST_DATA_DIR, "patch/delete_bnode_uri.rdp"), os.curdir
        )
        with open(delete_bnode_uri_path, "rb") as data:
            ds.parse(data, format="patch")
        assert len(ds) == 0

    def test_11(self):
        ds = Dataset()
        nq_path = os.path.relpath(
            os.path.join(TEST_DATA_DIR, "patch/add_and_delete_labeled_bnode_quads.rdp"),
            os.curdir,
        )
        with open(nq_path, "rb") as data:
            ds.parse(data, format="patch")
        assert len(ds) == 2
