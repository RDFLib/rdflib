from __future__ import annotations

from unittest.mock import Mock

import httpx
import pytest

from rdflib import Graph, URIRef
from rdflib.contrib.rdf4j import has_httpx
from rdflib.contrib.rdf4j.client import (
    Repository,
)

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping rdf4j tests, httpx not available"
)


@pytest.mark.parametrize(
    "graph_name, expected_params",
    [
        ["http://example.com/graph", {"graph": "http://example.com/graph"}],
        [URIRef("http://example.com/graph"), {"graph": "http://example.com/graph"}],
    ],
)
def test_repo_graph_store_get(
    repo: Repository,
    monkeypatch: pytest.MonkeyPatch,
    graph_name: str | URIRef,
    expected_params: dict[str, str],
):
    data = "<urn:a> <urn:b> <urn:c> ."
    mock_response = Mock(spec=httpx.Response, text=data)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)
    graph = repo.graphs.get(graph_name)
    headers = {"Accept": "application/n-triples"}
    mock_httpx_get.assert_called_once_with(
        "/repositories/test-repo/rdf-graphs/service",
        headers=headers,
        params=expected_params,
    )
    assert isinstance(graph, Graph)
    assert graph.isomorphic(Graph().parse(data=data))
    assert graph.identifier == URIRef(graph_name)


@pytest.mark.parametrize("graph_name", [None, ""])
def test_repo_graph_store_get_invalid_graph_name(
    repo: Repository, graph_name: str | None
):
    with pytest.raises(ValueError):
        repo.graphs.get(graph_name)  # type: ignore
