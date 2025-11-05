from __future__ import annotations

from unittest.mock import ANY, Mock

import httpx
import pytest

from rdflib import URIRef
from rdflib.contrib.rdf4j.client import (
    Repository,
)


@pytest.mark.parametrize(
    "graph_name, expected_params",
    [
        ["http://example.com/graph", {"graph": "http://example.com/graph"}],
        [URIRef("http://example.com/graph"), {"graph": "http://example.com/graph"}],
    ],
)
def test_repo_graph_store_overwrite(
    repo: Repository,
    monkeypatch: pytest.MonkeyPatch,
    graph_name: str | URIRef,
    expected_params: dict[str, str],
):
    data = "<urn:a> <urn:b> <urn:c> ."
    mock_response = Mock(spec=httpx.Response)
    mock_httpx_put = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "put", mock_httpx_put)
    repo.graphs.overwrite(graph_name, data)
    headers = {"Content-Type": "application/n-triples"}
    mock_httpx_put.assert_called_once_with(
        "/repositories/test-repo/rdf-graphs/service",
        headers=headers,
        params=expected_params,
        content=ANY,
    )


@pytest.mark.parametrize("graph_name", [None, ""])
def test_repo_graph_store_overwrite_invalid_graph_name(
    repo: Repository, graph_name: str | None
):
    with pytest.raises(ValueError):
        repo.graphs.overwrite(graph_name, "")  # type: ignore
