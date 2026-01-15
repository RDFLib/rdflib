from __future__ import annotations

from unittest.mock import Mock

import pytest

from rdflib.contrib.graphdb.exceptions import (
    ForbiddenError,
    InternalServerError,
    ResponseFormatError,
    ServiceUnavailableError,
    UnauthorisedError,
)
from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    import httpx

    from rdflib.contrib.graphdb.client import GraphDBClient
    from rdflib.contrib.graphdb.models import BackupOperationBean, SnapshotOptionsBean


def _make_valid_backup_response() -> dict:
    """Create a valid backup operation response dict."""
    return {
        "id": "backup-123",
        "username": "admin",
        "operation": "CREATE_BACKUP_IN_PROGRESS",
        "affectedRepositories": ["repo1", "repo2"],
        "msSinceCreated": 5000,
        "snapshotOptions": {
            "withRepositoryData": True,
            "withSystemData": True,
            "cleanDataDir": False,
            "repositories": ["repo1", "repo2"],
        },
        "nodePerformingClusterBackup": None,
    }


def test_backup_returns_backup_operation_bean(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that backup method returns a BackupOperationBean instance."""
    response_data = _make_valid_backup_response()
    mock_response = Mock(
        spec=httpx.Response,
        json=lambda: response_data,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.monitoring.backup()

    assert isinstance(result, BackupOperationBean)
    assert result.id == "backup-123"
    assert result.username == "admin"
    assert result.operation == "CREATE_BACKUP_IN_PROGRESS"
    assert result.affectedRepositories == ["repo1", "repo2"]
    assert result.msSinceCreated == 5000
    mock_httpx_get.assert_called_once_with(
        "/rest/monitor/backup",
        headers={"Accept": "application/json"},
    )


def test_backup_returns_nested_snapshot_options(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that backup method correctly parses nested snapshotOptions."""
    response_data = _make_valid_backup_response()
    mock_response = Mock(
        spec=httpx.Response,
        json=lambda: response_data,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.monitoring.backup()

    assert result is not None
    assert isinstance(result.snapshotOptions, SnapshotOptionsBean)
    assert result.snapshotOptions.withRepositoryData is True
    assert result.snapshotOptions.withSystemData is True
    assert result.snapshotOptions.cleanDataDir is False
    assert result.snapshotOptions.repositories == ["repo1", "repo2"]


def test_backup_returns_none_when_no_backup_in_progress(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that backup method returns None when response is empty."""
    mock_response = Mock(
        spec=httpx.Response,
        json=lambda: {},
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.monitoring.backup()

    assert result is None


def test_backup_returns_none_for_empty_list_response(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that backup method returns None when response is an empty list."""
    mock_response = Mock(
        spec=httpx.Response,
        json=lambda: [],
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.monitoring.backup()

    assert result is None


def test_backup_returns_none_for_null_response(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that backup method returns None when response is null."""
    mock_response = Mock(
        spec=httpx.Response,
        json=lambda: None,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.monitoring.backup()

    assert result is None


def test_backup_with_node_performing_cluster_backup(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that backup method handles nodePerformingClusterBackup correctly."""
    response_data = _make_valid_backup_response()
    response_data["nodePerformingClusterBackup"] = "node-1"
    mock_response = Mock(
        spec=httpx.Response,
        json=lambda: response_data,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.monitoring.backup()

    assert result is not None
    assert result.nodePerformingClusterBackup == "node-1"


@pytest.mark.parametrize(
    "operation",
    [
        "CREATE_BACKUP_IN_PROGRESS",
        "RESTORE_BACKUP_IN_PROGRESS",
        "CREATE_CLOUD_BACKUP_IN_PROGRESS",
        "RESTORE_CLOUD_BACKUP_IN_PROGRESS",
    ],
)
def test_backup_handles_all_valid_operations(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    operation: str,
):
    """Test that backup method handles all valid operation types."""
    response_data = _make_valid_backup_response()
    response_data["operation"] = operation
    mock_response = Mock(
        spec=httpx.Response,
        json=lambda: response_data,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.monitoring.backup()

    assert result is not None
    assert result.operation == operation


@pytest.mark.parametrize(
    "status_code, exception_class, match_message",
    [
        (401, UnauthorisedError, "Request is unauthorised"),
        (403, ForbiddenError, "Request is forbidden"),
        (500, InternalServerError, "Internal server error"),
        (503, ServiceUnavailableError, "Service is unavailable"),
    ],
)
def test_backup_raises_exceptions_for_error_status_codes(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
    exception_class: type,
    match_message: str,
):
    """Test that backup method raises appropriate exceptions for error responses."""
    mock_response = Mock(
        spec=httpx.Response,
        status_code=status_code,
        text="Server error message",
    )
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        f"HTTP {status_code}",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(exception_class, match=match_message):
        client.monitoring.backup()


@pytest.mark.parametrize(
    "status_code",
    [400, 404, 409, 502],
)
def test_backup_reraises_other_http_errors(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
):
    """Test that backup method re-raises HTTPStatusError for unhandled status codes."""
    mock_response = Mock(
        spec=httpx.Response,
        status_code=status_code,
        text="Error",
    )
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        f"HTTP {status_code}",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(httpx.HTTPStatusError):
        client.monitoring.backup()


def test_backup_raises_response_format_error_for_invalid_json(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that backup method raises ResponseFormatError when JSON parsing fails."""
    mock_response = Mock(spec=httpx.Response)
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(ResponseFormatError, match="Failed to parse response"):
        client.monitoring.backup()


@pytest.mark.parametrize(
    "invalid_response",
    [
        {"id": "backup-123"},  # Missing required fields
        {"id": "backup-123", "username": "admin"},  # Missing more fields
        {
            "id": "backup-123",
            "username": "admin",
            "operation": "CREATE_BACKUP_IN_PROGRESS",
        },  # Missing fields
        {
            "id": "backup-123",
            "username": "admin",
            "operation": "INVALID_OPERATION",
            "affectedRepositories": ["repo1"],
            "msSinceCreated": 5000,
            "snapshotOptions": {
                "withRepositoryData": True,
                "withSystemData": True,
                "cleanDataDir": False,
            },
        },  # Invalid operation
        {"snapshotOptions": "invalid"},  # Invalid snapshotOptions type
        "not a dict",  # String instead of dict
    ],
)
def test_backup_raises_response_format_error_for_invalid_structure(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    invalid_response,
):
    """Test that backup method raises ResponseFormatError for invalid response structure."""
    mock_response = Mock(
        spec=httpx.Response,
        json=lambda: invalid_response,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(ResponseFormatError, match="Failed to parse response"):
        client.monitoring.backup()


def test_backup_handles_empty_affected_repositories(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that backup method handles empty affectedRepositories list."""
    response_data = _make_valid_backup_response()
    response_data["affectedRepositories"] = []
    mock_response = Mock(
        spec=httpx.Response,
        json=lambda: response_data,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.monitoring.backup()

    assert result is not None
    assert result.affectedRepositories == []


def test_backup_handles_none_repositories_in_snapshot_options(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that backup method handles None repositories in snapshotOptions."""
    response_data = _make_valid_backup_response()
    response_data["snapshotOptions"]["repositories"] = None
    mock_response = Mock(
        spec=httpx.Response,
        json=lambda: response_data,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.monitoring.backup()

    assert result is not None
    assert result.snapshotOptions.repositories is None
