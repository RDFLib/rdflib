from __future__ import annotations

import httpx
import pytest

from rdflib.contrib.rdf4j import RDF4JClient
from rdflib.contrib.rdf4j.client import Repository, RepositoryManager


@pytest.fixture(scope="function")
def client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(RDF4JClient, "protocol", 12)
    with RDF4JClient("http://localhost/", auth=("admin", "admin")) as client:
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
