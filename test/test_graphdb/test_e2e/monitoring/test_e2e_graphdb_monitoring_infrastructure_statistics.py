from __future__ import annotations

import pytest

from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    from rdflib.contrib.graphdb import GraphDBClient
    from rdflib.contrib.graphdb.models import (
        InfrastructureMemoryUsage,
        InfrastructureStatistics,
        InfrastructureStorageMemory,
    )


@pytest.mark.testcontainer
def test_graphdb_monitoring_infrastructure_returns_statistics(client: GraphDBClient):
    """Test that the infrastructure property returns an InfrastructureStatistics instance."""
    result = client.monitoring.infrastructure

    assert isinstance(result, InfrastructureStatistics)


@pytest.mark.testcontainer
def test_graphdb_monitoring_infrastructure_has_valid_types(client: GraphDBClient):
    """Test that all fields have the correct types."""
    result = client.monitoring.infrastructure

    assert isinstance(result.heapMemoryUsage, InfrastructureMemoryUsage)
    assert isinstance(result.nonHeapMemoryUsage, InfrastructureMemoryUsage)
    assert isinstance(result.storageMemory, InfrastructureStorageMemory)
    assert isinstance(result.threadCount, int)
    assert isinstance(result.cpuLoad, float)
    assert isinstance(result.classCount, int)
    assert isinstance(result.gcCount, int)
    assert isinstance(result.openFileDescriptors, int)
    assert isinstance(result.maxFileDescriptors, int)


@pytest.mark.testcontainer
def test_graphdb_monitoring_infrastructure_memory_usage_types(client: GraphDBClient):
    """Test that memory usage nested objects have correct field types."""
    result = client.monitoring.infrastructure

    assert isinstance(result.heapMemoryUsage.max, int)
    assert isinstance(result.heapMemoryUsage.committed, int)
    assert isinstance(result.heapMemoryUsage.init, int)
    assert isinstance(result.heapMemoryUsage.used, int)

    assert isinstance(result.nonHeapMemoryUsage.max, int)
    assert isinstance(result.nonHeapMemoryUsage.committed, int)
    assert isinstance(result.nonHeapMemoryUsage.init, int)
    assert isinstance(result.nonHeapMemoryUsage.used, int)


@pytest.mark.testcontainer
def test_graphdb_monitoring_infrastructure_storage_memory_types(client: GraphDBClient):
    """Test that storage memory nested object has correct field types."""
    result = client.monitoring.infrastructure

    assert isinstance(result.storageMemory.dataDirUsed, int)
    assert isinstance(result.storageMemory.workDirUsed, int)
    assert isinstance(result.storageMemory.logsDirUsed, int)
    assert isinstance(result.storageMemory.dataDirFree, int)
    assert isinstance(result.storageMemory.workDirFree, int)
    assert isinstance(result.storageMemory.logsDirFree, int)


@pytest.mark.testcontainer
def test_graphdb_monitoring_infrastructure_values_are_non_negative(
    client: GraphDBClient,
):
    """Test that infrastructure statistics values are non-negative."""
    result = client.monitoring.infrastructure

    assert result.threadCount >= 0
    assert result.cpuLoad >= 0.0
    assert result.classCount >= 0
    assert result.gcCount >= 0
    assert result.openFileDescriptors >= 0
    assert result.maxFileDescriptors >= 0


@pytest.mark.testcontainer
def test_graphdb_monitoring_infrastructure_is_frozen(client: GraphDBClient):
    """Test that the returned InfrastructureStatistics instance is immutable."""
    result = client.monitoring.infrastructure

    with pytest.raises(AttributeError):
        result.threadCount = 999  # type: ignore


@pytest.mark.testcontainer
def test_graphdb_monitoring_infrastructure_multiple_calls(client: GraphDBClient):
    """Test that calling infrastructure multiple times returns consistent results."""
    result1 = client.monitoring.infrastructure
    result2 = client.monitoring.infrastructure

    assert isinstance(result1, InfrastructureStatistics)
    assert isinstance(result2, InfrastructureStatistics)

    assert isinstance(result1.threadCount, int)
    assert isinstance(result2.threadCount, int)
