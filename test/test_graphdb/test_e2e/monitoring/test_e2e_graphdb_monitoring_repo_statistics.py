from __future__ import annotations

import pytest

from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    from rdflib.contrib.graphdb import GraphDBClient
    from rdflib.contrib.graphdb.models import (
        RepositoryStatistics,
        RepositoryStatisticsEntityPool,
        RepositoryStatisticsQueries,
    )


@pytest.mark.testcontainer
def test_graphdb_monitoring_get_repo_stats_returns_statistics(client: GraphDBClient):
    """Test that get_repo_stats returns a RepositoryStatistics instance."""
    result = client.monitoring.get_repo_stats("test-repo")

    assert isinstance(result, RepositoryStatistics)
    assert isinstance(result.queries, RepositoryStatisticsQueries)
    assert isinstance(result.entityPool, RepositoryStatisticsEntityPool)
    assert isinstance(result.activeTransactions, int)
    assert isinstance(result.openConnections, int)


@pytest.mark.testcontainer
def test_graphdb_monitoring_get_repo_stats_queries_are_valid(client: GraphDBClient):
    """Test that the queries statistics have valid integer values."""
    result = client.monitoring.get_repo_stats("test-repo")

    assert isinstance(result.queries.slow, int)
    assert isinstance(result.queries.suboptimal, int)
    assert result.queries.slow >= 0
    assert result.queries.suboptimal >= 0


@pytest.mark.testcontainer
def test_graphdb_monitoring_get_repo_stats_entity_pool_is_valid(client: GraphDBClient):
    """Test that the entity pool statistics have valid integer values."""
    result = client.monitoring.get_repo_stats("test-repo")

    assert isinstance(result.entityPool.epoolReads, int)
    assert isinstance(result.entityPool.epoolWrites, int)
    assert isinstance(result.entityPool.epoolSize, int)
    assert result.entityPool.epoolReads >= 0
    assert result.entityPool.epoolWrites >= 0
    assert result.entityPool.epoolSize >= 0


@pytest.mark.testcontainer
def test_graphdb_monitoring_get_repo_stats_values_are_non_negative(
    client: GraphDBClient,
):
    """Test that all statistics values are non-negative."""
    result = client.monitoring.get_repo_stats("test-repo")

    assert result.activeTransactions >= 0
    assert result.openConnections >= 0


@pytest.mark.testcontainer
def test_graphdb_monitoring_get_repo_stats_is_frozen(client: GraphDBClient):
    """Test that the returned RepositoryStatistics instance is immutable."""
    result = client.monitoring.get_repo_stats("test-repo")

    with pytest.raises(AttributeError):
        result.activeTransactions = 999


@pytest.mark.testcontainer
def test_graphdb_monitoring_get_repo_stats_multiple_calls(client: GraphDBClient):
    """Test that calling get_repo_stats multiple times returns consistent results."""
    result1 = client.monitoring.get_repo_stats("test-repo")
    result2 = client.monitoring.get_repo_stats("test-repo")

    # Both should be valid RepositoryStatistics instances
    assert isinstance(result1, RepositoryStatistics)
    assert isinstance(result2, RepositoryStatistics)

    # Values may change between calls, but both should have valid types
    assert isinstance(result1.activeTransactions, int)
    assert isinstance(result2.activeTransactions, int)
    assert isinstance(result1.openConnections, int)
    assert isinstance(result2.openConnections, int)
