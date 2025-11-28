from __future__ import annotations

import pytest

from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping rdf4j tests, httpx not available"
)

if has_httpx:
    import httpx
    from rdflib.contrib.graphdb import GraphDBClient


@pytest.mark.testcontainer
def test_graphdb_ttyg(client: GraphDBClient):
    try:
        client.ttyg.query("test-agent", "test-tool", "test-query")
    except httpx.HTTPStatusError as err:
        assert err.response.status_code == 404
        assert err.response.text == "No such tool: test-tool"
