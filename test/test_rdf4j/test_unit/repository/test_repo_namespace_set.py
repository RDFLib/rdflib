from __future__ import annotations

from unittest.mock import Mock

import httpx
import pytest

from rdflib.contrib.rdf4j.client import Repository


@pytest.mark.parametrize(
    "prefix, namespace",
    [["test", "http://example.com/test"], ["test2", "http://example.com/test2"]],
)
def test_repo_namespace_set(
    repo: Repository,
    monkeypatch: pytest.MonkeyPatch,
    prefix: str,
    namespace: str,
):
    mock_response = Mock(spec=httpx.Response)
    mock_httpx_put = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "put", mock_httpx_put)
    repo.namespaces.set(prefix, namespace)
    mock_httpx_put.assert_called_once_with(
        f"/repositories/test-repo/namespaces/{prefix}",
        headers={"Content-Type": "text/plain"},
        content=namespace,
    )


@pytest.mark.parametrize(
    "prefix, namespace",
    [
        [None, "http://example.com/test"],
        ["test", None],
        ["", "http://example.com/test"],
        ["test", ""],
        [None, None],
        ["", ""],
    ],
)
def test_repo_namespace_set_error(
    repo: Repository, monkeypatch: pytest.MonkeyPatch, prefix: str, namespace: str
):
    with pytest.raises(ValueError):
        repo.namespaces.set(prefix, namespace)
