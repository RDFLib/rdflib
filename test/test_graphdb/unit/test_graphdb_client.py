from __future__ import annotations

import pytest

from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    import httpx

    from rdflib.contrib.graphdb import GraphDBClient
    from rdflib.contrib.graphdb.client import RepositoryManagement


def test_client_has_graphdb_rest_client(client: GraphDBClient):
    assert isinstance(client.graphdb_repositories, RepositoryManagement)


def test_client_accepts_httpx_timeout(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(GraphDBClient, "protocol", 12)
    timeout = httpx.Timeout(connect=1.0, read=2.0, write=3.0, pool=4.0)
    with GraphDBClient("http://localhost/", timeout=timeout) as client:
        client_timeout = client.http_client.timeout

    assert isinstance(client_timeout, httpx.Timeout)
    assert client_timeout.connect == timeout.connect
    assert client_timeout.read == timeout.read
    assert client_timeout.write == timeout.write
    assert client_timeout.pool == timeout.pool
