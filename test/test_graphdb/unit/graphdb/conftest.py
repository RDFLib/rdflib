from __future__ import annotations

from unittest.mock import Mock

import pytest

from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping rdf4j tests, httpx not available"
)

if has_httpx:
    import httpx

    from rdflib.contrib.graphdb import GraphDBClient
    from rdflib.contrib.graphdb.client import Repository, RepositoryManager


@pytest.fixture(scope="function")
def client(monkeypatch: pytest.MonkeyPatch, request):
    monkeypatch.setattr(GraphDBClient, "protocol", 12)
    with GraphDBClient("http://localhost/", auth=("admin", "admin")) as client:
        yield client
