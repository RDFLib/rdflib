from __future__ import annotations

import pytest

from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    from rdflib.contrib.graphdb import GraphDBClient
    from rdflib.contrib.graphdb.models import StructuresStatistics


@pytest.mark.testcontainer
def test_graphdb_monitoring_structures_returns_statistics(client: GraphDBClient):
    """Test that the structures property returns a StructuresStatistics instance."""
    result = client.monitoring.structures

    assert isinstance(result, StructuresStatistics)
    assert isinstance(result.cacheHit, int)
    assert isinstance(result.cacheMiss, int)


@pytest.mark.testcontainer
def test_graphdb_monitoring_structures_values_are_non_negative(client: GraphDBClient):
    """Test that the structures statistics values are non-negative."""
    result = client.monitoring.structures

    # Cache statistics should typically be non-negative
    assert result.cacheHit >= 0
    assert result.cacheMiss >= 0


@pytest.mark.testcontainer
def test_graphdb_monitoring_structures_is_frozen(client: GraphDBClient):
    """Test that the returned StructuresStatistics instance is immutable."""
    result = client.monitoring.structures

    with pytest.raises(AttributeError):
        result.cacheHit = 999  # type: ignore


@pytest.mark.testcontainer
def test_graphdb_monitoring_structures_multiple_calls(client: GraphDBClient):
    """Test that calling structures multiple times returns consistent results."""
    result1 = client.monitoring.structures
    result2 = client.monitoring.structures

    # Both should be valid StructuresStatistics instances
    assert isinstance(result1, StructuresStatistics)
    assert isinstance(result2, StructuresStatistics)

    # Values may change between calls, but both should have valid types
    assert isinstance(result1.cacheHit, int)
    assert isinstance(result2.cacheHit, int)
    assert isinstance(result1.cacheMiss, int)
    assert isinstance(result2.cacheMiss, int)
