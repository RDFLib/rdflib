from __future__ import annotations

import io
import typing as t
from pathlib import Path
from unittest.mock import Mock

import pytest

import rdflib.contrib.rdf4j.util
import rdflib.plugins.sparql.processor
from rdflib.contrib.rdf4j.util import (
    build_context_param,
    build_sparql_query_accept_header,
    rdf_payload_to_stream,
    validate_no_bnodes,
)
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID, Dataset, Graph
from rdflib.term import BNode, Literal, URIRef


@pytest.mark.parametrize(
    "graph_name, expected_graph_name_param",
    [
        [DATASET_DEFAULT_GRAPH_ID, "null"],
        ["http://example.com/graph", "<http://example.com/graph>"],
        [URIRef("http://example.com/graph"), "<http://example.com/graph>"],
        [BNode("some-bnode"), "_:some-bnode"],
        [
            [URIRef("http://example.com/graph"), BNode("some-bnode")],
            "<http://example.com/graph>,_:some-bnode",
        ],
        [None, None],
    ],
)
def test_build_context_param(graph_name, expected_graph_name_param):
    params = {}
    build_context_param(params, graph_name)
    if graph_name is None:
        assert "context" not in params
    else:
        assert params["context"] == expected_graph_name_param


@pytest.mark.parametrize(
    "data, expected_value_type, expected_should_close",
    [
        [
            open(Path(__file__), "rb"),
            io.BufferedReader,
            False,
        ],
        ["", io.BytesIO, False],
        [b"", io.BytesIO, False],
        [io.BytesIO(b""), io.BytesIO, False],
        [Graph(), io.BytesIO, True],
        [Dataset(), io.BytesIO, True],
    ],
)
def test_rdf_payload_to_stream(
    data: str | bytes | t.BinaryIO | Graph | Dataset,
    expected_value_type: type[io.BufferedIOBase | io.RawIOBase],
    expected_should_close: bool,
):
    value, should_close = rdf_payload_to_stream(data)
    assert isinstance(value, expected_value_type)
    assert should_close == expected_should_close


def test_build_sparql_query_accept_header(monkeypatch: pytest.MonkeyPatch):
    mock = Mock()
    mock.algebra.name = "InvalidQueryType"
    monkeypatch.setattr(rdflib.contrib.rdf4j.util, "prepareQuery", lambda _: mock)

    with pytest.raises(ValueError, match="Unsupported query type: InvalidQueryType"):
        build_sparql_query_accept_header("blah", {})


@pytest.mark.parametrize(
    "subj, pred, obj, graph_name",
    [
        [BNode(), None, None, None],
        [None, BNode(), None, None],
        [None, None, BNode(), None],
        [None, None, None, BNode()],
        [None, None, None, [BNode(), URIRef("http://example.com/graph")]],
    ],
)
def test_validate_no_bnodes(
    subj: URIRef | None,
    pred: URIRef | None,
    obj: URIRef | Literal | None,
    graph_name,
):
    with pytest.raises(ValueError, match="must not be a BNode"):
        validate_no_bnodes(subj, pred, obj, graph_name)
