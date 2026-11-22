from __future__ import annotations

import pytest

from rdflib.contrib.graphdb.exceptions import ServiceUnavailableError
from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    from rdflib.contrib.graphdb import GraphDBClient


@pytest.mark.testcontainer
def test_graphdb_monitoring_cluster_returns_string(client: GraphDBClient):
    """Test that the cluster method returns a string.

    We don't have clustering enabled. This should return 503.
    """
    with pytest.raises(ServiceUnavailableError):
        client.monitoring.cluster()
