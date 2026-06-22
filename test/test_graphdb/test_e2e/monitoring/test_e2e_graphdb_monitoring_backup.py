from __future__ import annotations

import pytest

from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    from rdflib.contrib.graphdb import GraphDBClient
    from rdflib.contrib.graphdb.models import BackupOperationBean, SnapshotOptionsBean


@pytest.mark.testcontainer
def test_graphdb_monitoring_backup_returns_none_when_no_backup(client: GraphDBClient):
    """Test that the backup method returns None when no backup is in progress.

    In a fresh GraphDB instance, there should be no backup operation running,
    so the method should return None.
    """
    result = client.monitoring.backup()

    assert result is None


@pytest.mark.testcontainer
def test_graphdb_monitoring_backup_method_is_callable(client: GraphDBClient):
    """Test that the backup method can be called without errors."""
    # This test verifies the method is accessible and callable
    # The result depends on whether a backup is in progress
    result = client.monitoring.backup()

    # Result should be either None or a BackupOperationBean
    assert result is None or isinstance(result, BackupOperationBean)


@pytest.mark.testcontainer
def test_graphdb_monitoring_backup_multiple_calls_consistent(client: GraphDBClient):
    """Test that calling backup multiple times returns consistent results.

    When no backup is in progress, multiple calls should all return None.
    """
    result1 = client.monitoring.backup()
    result2 = client.monitoring.backup()

    # Both should be None when no backup is running
    # or both should be BackupOperationBean instances
    assert (result1 is None) == (result2 is None)


@pytest.mark.testcontainer
def test_graphdb_monitoring_backup_returns_valid_bean_if_backup_exists(
    client: GraphDBClient,
):
    """Test that a BackupOperationBean has valid structure if returned.

    If a backup is in progress (unlikely in test environment),
    validate the returned bean has expected attributes.
    """
    result = client.monitoring.backup()

    if result is not None:
        assert isinstance(result, BackupOperationBean)
        assert isinstance(result.id, str)
        assert isinstance(result.username, str)
        assert isinstance(result.operation, str)
        assert isinstance(result.affectedRepositories, list)
        assert all(isinstance(r, str) for r in result.affectedRepositories)
        assert isinstance(result.msSinceCreated, int)
        assert isinstance(result.snapshotOptions, SnapshotOptionsBean)
