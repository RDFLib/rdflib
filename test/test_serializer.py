import logging
import unittest
from rdflib import RDF, Graph, Literal, Namespace, URIRef
from tempfile import TemporaryDirectory
from pathlib import Path, PurePath

from typing import Tuple, cast

import pytest
import itertools

from rdflib.graph import ConjunctiveGraph

from .testutils import GraphHelper


@pytest.mark.parametrize(
    "format, tuple_index, is_keyword",
    [
        (format, tuple_index, keyword)
        for format, (tuple_index, keyword) in itertools.product(
            ["turtle", "n3", "trig"],
            [
                (0, False),
                (1, True),
                (2, False),
            ],
        )
    ]
    + [("trig", 3, False)],
)
def test_rdf_type(format: str, tuple_index: int, is_keyword: bool) -> None:
    NS = Namespace("example:")
    graph = ConjunctiveGraph()
    graph.bind("eg", NS)
    nodes = [NS.subj, NS.pred, NS.obj, NS.graph]
    nodes[tuple_index] = RDF.type
    quad = cast(Tuple[URIRef, URIRef, URIRef, URIRef], tuple(nodes))
    graph.add(quad)
    data = graph.serialize(format=format)
    logging.info("data = %s", data)
    assert NS in data
    if is_keyword:
        assert str(RDF) not in data
    else:
        assert str(RDF) in data
    parsed_graph = ConjunctiveGraph()
    parsed_graph.parse(data=data, format=format)
    GraphHelper.assert_triple_sets_equals(graph, parsed_graph)


class TestSerialize(unittest.TestCase):
    def setUp(self) -> None:

        graph = Graph()
        subject = URIRef("example:subject")
        predicate = URIRef("example:predicate")
        object = Literal("日本語の表記体系", lang="jpx")
        self.triple = (
            subject,
            predicate,
            object,
        )
        graph.add(self.triple)
        self.graph = graph
        return super().setUp()

    def test_serialize_to_purepath(self):
        with TemporaryDirectory() as td:
            tfpath = PurePath(td) / "out.nt"
            self.graph.serialize(destination=tfpath, format="nt", encoding="utf-8")
            graph_check = Graph()
            graph_check.parse(source=tfpath, format="nt")

        self.assertEqual(self.triple, next(iter(graph_check)))

    def test_serialize_to_path(self):
        with TemporaryDirectory() as td:
            tfpath = Path(td) / "out.nt"
            self.graph.serialize(destination=tfpath, format="nt", encoding="utf-8")
            graph_check = Graph()
            graph_check.parse(source=tfpath, format="nt")

        self.assertEqual(self.triple, next(iter(graph_check)))

    def test_serialize_to_neturl(self):
        with self.assertRaises(ValueError) as raised:
            self.graph.serialize(
                destination="http://example.com/", format="nt", encoding="utf-8"
            )
        self.assertIn("destination", f"{raised.exception}")

    def test_serialize_to_fileurl(self):
        with TemporaryDirectory() as td:
            tfpath = Path(td) / "out.nt"
            tfurl = tfpath.as_uri()
            self.assertRegex(tfurl, r"^file:")
            self.assertFalse(tfpath.exists())
            self.graph.serialize(destination=tfurl, format="nt", encoding="utf-8")
            self.assertTrue(tfpath.exists())
            graph_check = Graph()
            graph_check.parse(source=tfpath, format="nt")
        self.assertEqual(self.triple, next(iter(graph_check)))
