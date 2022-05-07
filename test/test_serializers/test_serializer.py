import itertools
import logging
import re
from pathlib import Path
from test.utils import GraphHelper
from typing import Tuple, cast

import pytest

from rdflib import RDF, Graph, Literal, Namespace, URIRef
from rdflib.graph import ConjunctiveGraph


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


EG = Namespace("example:")


@pytest.fixture
def simple_graph() -> Graph:
    graph = Graph()
    graph.add((EG.subject, EG.predicate, Literal("日本語の表記体系", lang="jpx")))
    return graph


def test_serialize_to_purepath(tmp_path: Path, simple_graph: Graph):
    tfpath = tmp_path / "out.nt"
    simple_graph.serialize(destination=tfpath, format="nt", encoding="utf-8")
    graph_check = Graph()
    graph_check.parse(source=tfpath, format="nt")

    GraphHelper.assert_triple_sets_equals(simple_graph, graph_check)


def test_serialize_to_path(tmp_path: Path, simple_graph: Graph):
    tfpath = tmp_path / "out.nt"
    simple_graph.serialize(destination=tfpath, format="nt", encoding="utf-8")
    graph_check = Graph()
    graph_check.parse(source=tfpath, format="nt")

    GraphHelper.assert_triple_sets_equals(simple_graph, graph_check)


def test_serialize_to_neturl(simple_graph: Graph):
    with pytest.raises(ValueError) as raised:
        simple_graph.serialize(
            destination="http://example.com/", format="nt", encoding="utf-8"
        )
    assert "destination" in f"{raised.value}"


def test_serialize_to_fileurl(tmp_path: Path, simple_graph: Graph):
    tfpath = tmp_path / "out.nt"
    tfurl = tfpath.as_uri()
    assert re.match(r"^file:", tfurl)
    assert not tfpath.exists()
    simple_graph.serialize(destination=tfurl, format="nt", encoding="utf-8")
    assert tfpath.exists()
    graph_check = Graph()
    graph_check.parse(source=tfpath, format="nt")
    GraphHelper.assert_triple_sets_equals(simple_graph, graph_check)
