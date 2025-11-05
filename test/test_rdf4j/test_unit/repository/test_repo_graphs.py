from __future__ import annotations

from unittest.mock import Mock

import httpx
import pytest

from rdflib.contrib.rdf4j.client import Repository
from rdflib.contrib.rdf4j.exceptions import RepositoryFormatError
from rdflib.term import BNode, IdentifiedNode, URIRef


@pytest.mark.parametrize(
    "response_dict, expected_result",
    [
        [{"results": {"bindings": []}}, set()],
        [
            {
                "results": {
                    "bindings": [
                        {
                            "contextID": {
                                "value": "http://example.com/graph",
                                "type": "uri",
                            }
                        }
                    ]
                }
            },
            {URIRef("http://example.com/graph")},
        ],
        [
            {
                "results": {
                    "bindings": [{"contextID": {"value": "bnode1", "type": "bnode"}}]
                }
            },
            {BNode("bnode1")},
        ],
        [
            {
                "results": {
                    "bindings": [
                        {"contextID": {"value": "bnode1", "type": "bnode"}},
                        {"contextID": {"value": "urn:blah", "type": "uri"}},
                    ]
                }
            },
            {BNode("bnode1"), URIRef("urn:blah")},
        ],
    ],
)
def test_repo_graphs(
    repo: Repository,
    monkeypatch: pytest.MonkeyPatch,
    response_dict: dict,
    expected_result: set[IdentifiedNode],
):
    """Test that the graphs are returned correctly."""
    mock_response = Mock(spec=httpx.Response, json=lambda: response_dict)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)
    result = repo.graph_names()
    mock_httpx_get.assert_called_once_with(
        "/repositories/test-repo/contexts",
        headers={"Accept": "application/sparql-results+json"},
    )
    assert set(result) == expected_result


@pytest.mark.parametrize(
    "response_dict, expected_error",
    [
        [{}, RepositoryFormatError],
        [
            {
                "results": {
                    "bindings": [
                        {"contextID": {"type": "invalid", "value": "urn:example"}}
                    ]
                }
            },
            RepositoryFormatError,
        ],
    ],
)
def test_repo_graphs_invalid_response(
    repo: Repository,
    monkeypatch: pytest.MonkeyPatch,
    response_dict: dict,
    expected_error: type[Exception],
):
    """Test that an error is raised when the response is invalid."""
    mock_response = Mock(spec=httpx.Response, json=lambda: response_dict)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)
    with pytest.raises(expected_error):
        repo.graph_names()
    mock_httpx_get.assert_called_once_with(
        "/repositories/test-repo/contexts",
        headers={"Accept": "application/sparql-results+json"},
    )
