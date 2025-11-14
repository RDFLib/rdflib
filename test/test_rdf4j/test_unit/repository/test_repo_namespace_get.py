from __future__ import annotations

from unittest.mock import Mock

import pytest

from rdflib import Dataset, URIRef
from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping rdf4j tests, httpx not available"
)

if has_httpx:
    import httpx

    from rdflib.contrib.rdf4j.client import (
        NamespaceListingResult,
        RDF4JNamespaceManager,
        Repository,
    )


@pytest.mark.parametrize(
    "prefix, response_text, response_status_code, expected_value",
    [
        [
            "skos",
            "http://www.w3.org/2004/02/skos/core#",
            200,
            "http://www.w3.org/2004/02/skos/core#",
        ],
        ["non-existent", "Undefined prefix: non-existent", 404, None],
    ],
)
def test_repo_namespace_get(
    repo: Repository,
    monkeypatch: pytest.MonkeyPatch,
    prefix: str,
    response_text: str,
    response_status_code: int,
    expected_value: str | None,
):
    mock_response = Mock(spec=httpx.Response)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)
    repo.namespaces.get(prefix)
    mock_httpx_get.assert_called_once_with(
        f"/repositories/test-repo/namespaces/{prefix}",
        headers={"Accept": "text/plain"},
    )


@pytest.mark.parametrize("prefix", [None, ""])
def test_repo_namespace_get_error(
    repo: Repository, monkeypatch: pytest.MonkeyPatch, prefix: str | None
):
    mock_response = Mock(spec=httpx.Response)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)
    with pytest.raises(ValueError):
        repo.namespaces.get(prefix)  # type: ignore


def test_repo_get_with_namespace_binding(
    repo: Repository, monkeypatch: pytest.MonkeyPatch
):
    mock_response = Mock(spec=httpx.Response, text="")
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)
    monkeypatch.setattr(
        RDF4JNamespaceManager,
        "list",
        lambda _: [
            NamespaceListingResult(prefix="test", namespace="http://example.org/test/")
        ],
    )
    ds = repo.get()
    assert isinstance(ds, Dataset)
    assert ("test", URIRef("http://example.org/test/")) in set(ds.namespaces())
