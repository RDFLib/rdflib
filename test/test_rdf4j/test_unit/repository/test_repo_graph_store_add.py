from __future__ import annotations

from unittest.mock import ANY, Mock

import httpx
import pytest

from rdflib import URIRef
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
def test_repo_graph_store_add(
    repo: Repository,
    monkeypatch: pytest.MonkeyPatch,
    graph_name: str | URIRef,
    expected_params: dict[str, str],
):
    data = "<urn:a> <urn:b> <urn:c> ."
    mock_response = Mock(spec=httpx.Response, text=data)
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)
    repo.graphs.add(graph_name, data)
    headers = {"Content-Type": "application/n-triples"}
    mock_httpx_post.assert_called_once_with(
        "/repositories/test-repo/rdf-graphs/service",
        headers=headers,
        params=expected_params,
        content=ANY,
    )


@pytest.mark.parametrize("graph_name", [None, ""])
def test_repo_graph_store_add_invalid_graph_name(
    repo: Repository, graph_name: str | None
):
    with pytest.raises(ValueError):
        repo.graphs.add(graph_name, "")  # type: ignore
