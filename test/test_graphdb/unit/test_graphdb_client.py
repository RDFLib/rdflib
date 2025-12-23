from __future__ import annotations

import pytest

from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    from rdflib.contrib.graphdb import GraphDBClient
    from rdflib.contrib.graphdb.client import RepositoryManagement


def test_client_has_graphdb_rest_client(client: GraphDBClient):
    assert isinstance(client.repos, RepositoryManagement)
