from __future__ import annotations

from unittest.mock import Mock

import pytest

from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping rdf4j tests, httpx not available"
)

if has_httpx:
    import httpx

    from rdflib.contrib.rdf4j import RDF4JClient
    from rdflib.contrib.rdf4j.client import Repository, RepositoryManager
    from rdflib.contrib.graphdb import GraphDBClient


@pytest.fixture(scope="function", params=[RDF4JClient, GraphDBClient])
def client(monkeypatch: pytest.MonkeyPatch, request):
    monkeypatch.setattr(RDF4JClient, "protocol", 12)
    with request.param("http://localhost/", auth=("admin", "admin")) as client:
        yield client


@pytest.fixture(scope="function")
def repo(client: RDF4JClient, monkeypatch: pytest.MonkeyPatch):
    with httpx.Client() as http_client:
        monkeypatch.setattr(
            RepositoryManager,
            "create",
            lambda *args, **kwargs: Repository("test-repo", http_client),
        )

        repo = client.repositories.create("test-repo", "")
        assert repo.identifier == "test-repo"
        yield repo


@pytest.fixture
def txn(repo: Repository, monkeypatch: pytest.MonkeyPatch):
    transaction_url = "http://example.com/transaction/1"
    mock_transaction_create_response = Mock(
        spec=httpx.Response, headers={"Location": transaction_url}
    )
    mock_httpx_post = Mock(return_value=mock_transaction_create_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)
    with repo.transaction() as txn:
        yield txn
        mock_commit_response = Mock(spec=httpx.Response, status_code=200)
        mock_httpx_put = Mock(return_value=mock_commit_response)
        monkeypatch.setattr(httpx.Client, "put", mock_httpx_put)
