import pathlib

import pytest
import httpx

from rdflib.rdf4j import RDF4JClient
from rdflib.rdf4j.client import (
    RepositoryAlreadyExistsError,
    RepositoryNotFoundError,
    RepositoryFormatError,
    RepositoryNotHealthyError,
)

# TODO: only run these tests on py39 or greater. Testcontainers not available on py38.

def test_repos(client: RDF4JClient):
    assert client.repositories.list() == []


def test_list_repo_non_existent(client: RDF4JClient):
    assert client.repositories.list() == []
    with pytest.raises(RepositoryNotFoundError):
        assert client.repositories.get("non-existent") is None


def test_list_repo_format_error(client: RDF4JClient, monkeypatch):
    class MockResponse:
        def json(self):
            return {}

        def raise_for_status(self):
            pass

    monkeypatch.setattr(httpx.Client, "get", lambda *args, **kwargs: MockResponse())
    with pytest.raises(RepositoryFormatError):
        client.repositories.list()


def test_repo_manager_crud(client: RDF4JClient):
    # Empty state
    assert client.repositories.list() == []

    config_path = pathlib.Path(__file__).parent / "repo-configs/test-repo-config.ttl"
    with open(config_path) as file:
        config = file.read()

    repo = client.repositories.create("test-repo", config)
    assert repo.identifier == "test-repo"
    assert repo.health()

    # New repository created
    assert len(client.repositories.list()) == 1

    # Repo already exists error
    with pytest.raises(RepositoryAlreadyExistsError):
        client.repositories.create("test-repo", config)

    # Delete repository
    client.repositories.delete("test-repo")
    assert client.repositories.list() == []

    # Deleting non-existent repo
    with pytest.raises(RepositoryNotFoundError):
        client.repositories.delete("test-repo")


def test_repo_not_healthy(client: RDF4JClient, monkeypatch):
    config_path = pathlib.Path(__file__).parent / "repo-configs/test-repo-config.ttl"
    with open(config_path) as file:
        config = file.read()

    repo = client.repositories.create("test-repo", config)
    assert repo.identifier == "test-repo"

    class MockResponse:
        def raise_for_status(self):
            raise httpx.HTTPStatusError(
                "",
                request=httpx.Request("post", ""),
                response=httpx.Response(status_code=500),
            )

    monkeypatch.setattr(httpx.Client, "post", lambda *args, **kwargs: MockResponse())
    with pytest.raises(RepositoryNotHealthyError):
        repo.health()
