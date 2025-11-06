from __future__ import annotations

from unittest.mock import Mock

import httpx
import pytest

from rdflib.contrib.rdf4j.client import (
    Repository,
)


def test_repo_update(repo: Repository, monkeypatch: pytest.MonkeyPatch):
    mock_response = Mock(spec=httpx.Response, status_code=204)
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)
    repo.update(
        "insert data { <http://example.org/s> <http://example.org/p> <http://example.org/o> }"
    )
    mock_httpx_post.assert_called_once_with(
        "/repositories/test-repo",
        headers={"Content-Type": "application/sparql-update"},
        content="insert data { <http://example.org/s> <http://example.org/p> <http://example.org/o> }",
    )
