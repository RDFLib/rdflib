import pathlib

import httpx
import pytest

from rdflib.contrib.graphdb import GraphDBClient
from rdflib.contrib.rdf4j.exceptions import (
    RepositoryAlreadyExistsError,
    RepositoryNotFoundError,
    RepositoryNotHealthyError,
)

# TODO: consider parameterizing the client (RDF4JClient, GraphDBClient)


def test_repo_manager_crud(client: GraphDBClient):
    # Empty state
    assert client.repositories.list() == []

    config_path = (
        pathlib.Path(__file__).parent.parent / "repo-configs/test-repo-config.ttl"
    )
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


def test_repo_not_healthy(client: GraphDBClient, monkeypatch):
    config_path = (
        pathlib.Path(__file__).parent.parent / "repo-configs/test-repo-config.ttl"
    )
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
