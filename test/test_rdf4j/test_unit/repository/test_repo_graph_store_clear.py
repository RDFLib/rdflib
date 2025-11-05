from __future__ import annotations

from unittest.mock import Mock

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
def test_repo_graph_store_add(
    repo: Repository,
    monkeypatch: pytest.MonkeyPatch,
    graph_name: str | URIRef,
    expected_params: dict[str, str],
):
    mock_response = Mock(spec=httpx.Response)
    mock_httpx_delete = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "delete", mock_httpx_delete)
    repo.graphs.clear(graph_name)
    mock_httpx_delete.assert_called_once_with(
        "/repositories/test-repo/rdf-graphs/service",
        params=expected_params,
    )


@pytest.mark.parametrize("graph_name", [None, ""])
def test_repo_graph_store_clear_invalid_graph_name(
    repo: Repository, graph_name: str | None
):
    with pytest.raises(ValueError):
        repo.graphs.clear(graph_name)  # type: ignore
