from __future__ import annotations

import pytest

from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping rdf4j tests, httpx not available"
)

if has_httpx:
    from rdflib.contrib.graphdb import GraphDBClient


@pytest.mark.testcontainer
def test_graphdb_repository_restart(client: GraphDBClient):
    result = client.repos.restart("test-repo")
    assert result == ""
