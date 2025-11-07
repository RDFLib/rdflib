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


@pytest.mark.parametrize(
    "prefix",
    [
        ["skos"],
        ["schema"],
    ],
)
def test_repo_namespace_remove(
    repo: Repository,
    monkeypatch: pytest.MonkeyPatch,
    prefix: str,
):
    mock_response = Mock(spec=httpx.Response)
    mock_httpx_remove = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "delete", mock_httpx_remove)
    repo.namespaces.remove(prefix)
    mock_httpx_remove.assert_called_once_with(
        f"/repositories/test-repo/namespaces/{prefix}",
    )


@pytest.mark.parametrize("prefix", [None, ""])
def test_repo_namespace_remove_error(
    repo: Repository, monkeypatch: pytest.MonkeyPatch, prefix: str | None
):
    mock_response = Mock(spec=httpx.Response)
    mock_httpx_remove = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "delete", mock_httpx_remove)
    with pytest.raises(ValueError):
        repo.namespaces.remove(prefix)  # type: ignore
