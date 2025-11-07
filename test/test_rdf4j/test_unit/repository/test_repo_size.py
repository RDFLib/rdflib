from __future__ import annotations

import typing as t
from unittest.mock import Mock

import httpx
import pytest

from rdflib.contrib.rdf4j import has_httpx
from rdflib.contrib.rdf4j.client import (
    Repository,
)
from rdflib.contrib.rdf4j.exceptions import RepositoryFormatError
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID
from rdflib.term import BNode, IdentifiedNode, URIRef

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping rdf4j tests, httpx not available"
)


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
def test_repo_size_graph_name(
    repo: Repository,
    monkeypatch: pytest.MonkeyPatch,
    graph_name: IdentifiedNode | t.Iterable[IdentifiedNode] | str | None,
    expected_graph_name_param: str,
):
    """
    Test that graph_name is passed as a query parameter and correctly handles the
    different type variations.
    """
    mock_response = Mock(spec=httpx.Response, text="0")
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)
    if graph_name is None:
        params = {}
    else:
        params = {"context": expected_graph_name_param}
    size = repo.size(graph_name=graph_name)
    mock_httpx_get.assert_called_once_with(
        "/repositories/test-repo/size",
        params=params,
    )
    assert size == 0


@pytest.mark.parametrize(
    "response_value, expected_parsed_value",
    [
        ["0", 0],
        ["123", 123],
        ["-100", RepositoryFormatError],
        ["foo", RepositoryFormatError],
    ],
)
def test_repo_size_values(
    repo: Repository,
    monkeypatch: pytest.MonkeyPatch,
    response_value: str,
    expected_parsed_value: int | type[RepositoryFormatError],
):
    """Test that the return value of the response is correctly parsed."""
    mock_response = Mock(spec=httpx.Response, text=response_value)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    if isinstance(expected_parsed_value, int):
        size = repo.size()
        assert size == expected_parsed_value
    else:
        with pytest.raises(expected_parsed_value):
            repo.size()

    mock_httpx_get.assert_called_once_with(
        "/repositories/test-repo/size",
        params={},
    )
