from __future__ import annotations

from unittest.mock import Mock

import pytest

from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping rdf4j tests, httpx not available"
)

if has_httpx:
    import httpx

    from rdflib.contrib.rdf4j.client import Repository


def test_repo_namespace_clear(repo: Repository, monkeypatch: pytest.MonkeyPatch):
    mock_response = Mock(spec=httpx.Response)
    mock_httpx_delete = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "delete", mock_httpx_delete)
    repo.namespaces.clear()
    mock_httpx_delete.assert_called_once_with(
        "/repositories/test-repo/namespaces",
        headers={"Accept": "application/sparql-results+json"},
    )
