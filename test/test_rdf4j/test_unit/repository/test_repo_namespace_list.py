from __future__ import annotations

from unittest.mock import Mock

import httpx
import pytest

from rdflib.contrib.rdf4j import has_httpx
from rdflib.contrib.rdf4j.client import NamespaceListingResult, Repository
from rdflib.contrib.rdf4j.exceptions import RepositoryFormatError
from rdflib.term import IdentifiedNode

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping rdf4j tests, httpx not available"
)


@pytest.mark.parametrize(
    "response_dict, expected_result",
    [
        [{"results": {"bindings": []}}, set()],
        [
            {
                "results": {
                    "bindings": [
                        {
                            "prefix": {"value": "test"},
                            "namespace": {"value": "http://example.com/test/"},
                        },
                        {
                            "prefix": {"value": "test2"},
                            "namespace": {"value": "http://example.com/test2/"},
                        },
                    ]
                }
            },
            {
                NamespaceListingResult(
                    prefix="test", namespace="http://example.com/test/"
                ),
                NamespaceListingResult(
                    prefix="test2", namespace="http://example.com/test2/"
                ),
            },
        ],
    ],
)
def test_repo_namespace_list(
    repo: Repository,
    monkeypatch: pytest.MonkeyPatch,
    response_dict: dict,
    expected_result: set[IdentifiedNode],
):
    mock_response = Mock(spec=httpx.Response, json=lambda: response_dict)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)
    result = repo.namespaces.list()
    assert set(result) == expected_result
    mock_httpx_get.assert_called_once_with(
        "/repositories/test-repo/namespaces",
        headers={"Accept": "application/sparql-results+json"},
    )


def test_repo_namespace_list_error(repo: Repository, monkeypatch: pytest.MonkeyPatch):
    response_dict: dict[str, str] = {}

    mock_response = Mock(spec=httpx.Response, json=lambda: response_dict)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)
    with pytest.raises(RepositoryFormatError):
        repo.namespaces.list()
    mock_httpx_get.assert_called_once_with(
        "/repositories/test-repo/namespaces",
        headers={"Accept": "application/sparql-results+json"},
    )
