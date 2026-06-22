from __future__ import annotations

from unittest.mock import Mock

import pytest

from rdflib.contrib.graphdb.exceptions import (
    ForbiddenError,
    InternalServerError,
    ResponseFormatError,
    UnauthorisedError,
)
from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    import httpx

    from rdflib.contrib.graphdb.client import GraphDBClient
    from rdflib.contrib.graphdb.models import InfrastructureStatistics


def _make_valid_infrastructure_response() -> dict:
    """Create a valid infrastructure statistics response dict."""
    return {
        "heapMemoryUsage": {"max": 1000, "committed": 800, "init": 500, "used": 600},
        "nonHeapMemoryUsage": {"max": 500, "committed": 400, "init": 200, "used": 300},
        "storageMemory": {
            "dataDirUsed": 1000,
            "workDirUsed": 500,
            "logsDirUsed": 200,
            "dataDirFree": 9000,
            "workDirFree": 9500,
            "logsDirFree": 9800,
        },
        "threadCount": 50,
        "cpuLoad": 0.75,
        "classCount": 1000,
        "gcCount": 25,
        "openFileDescriptors": 100,
        "maxFileDescriptors": 1024,
    }


def test_infrastructure_returns_infrastructure_statistics(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that infrastructure property returns an InfrastructureStatistics instance."""
    response_data = _make_valid_infrastructure_response()
    mock_response = Mock(
        spec=httpx.Response,
        json=lambda: response_data,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.monitoring.infrastructure

    assert isinstance(result, InfrastructureStatistics)
    assert result.threadCount == 50
    assert result.cpuLoad == 0.75
    assert result.classCount == 1000
    assert result.gcCount == 25
    assert result.openFileDescriptors == 100
    assert result.maxFileDescriptors == 1024
    mock_httpx_get.assert_called_once_with(
        "/rest/monitor/infrastructure",
        headers={"Accept": "application/json"},
    )


def test_infrastructure_returns_nested_memory_usage(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that infrastructure property correctly parses nested memory usage objects."""
    response_data = _make_valid_infrastructure_response()
    mock_response = Mock(
        spec=httpx.Response,
        json=lambda: response_data,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.monitoring.infrastructure

    assert result.heapMemoryUsage.max == 1000
    assert result.heapMemoryUsage.committed == 800
    assert result.heapMemoryUsage.init == 500
    assert result.heapMemoryUsage.used == 600
    assert result.nonHeapMemoryUsage.max == 500
    assert result.nonHeapMemoryUsage.committed == 400
    assert result.nonHeapMemoryUsage.init == 200
    assert result.nonHeapMemoryUsage.used == 300


def test_infrastructure_returns_nested_storage_memory(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that infrastructure property correctly parses nested storage memory objects."""
    response_data = _make_valid_infrastructure_response()
    mock_response = Mock(
        spec=httpx.Response,
        json=lambda: response_data,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.monitoring.infrastructure

    assert result.storageMemory.dataDirUsed == 1000
    assert result.storageMemory.workDirUsed == 500
    assert result.storageMemory.logsDirUsed == 200
    assert result.storageMemory.dataDirFree == 9000
    assert result.storageMemory.workDirFree == 9500
    assert result.storageMemory.logsDirFree == 9800


def test_infrastructure_returns_zero_values(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that infrastructure property handles zero values correctly."""
    response_data = {
        "heapMemoryUsage": {"max": 0, "committed": 0, "init": 0, "used": 0},
        "nonHeapMemoryUsage": {"max": 0, "committed": 0, "init": 0, "used": 0},
        "storageMemory": {
            "dataDirUsed": 0,
            "workDirUsed": 0,
            "logsDirUsed": 0,
            "dataDirFree": 0,
            "workDirFree": 0,
            "logsDirFree": 0,
        },
        "threadCount": 0,
        "cpuLoad": 0.0,
        "classCount": 0,
        "gcCount": 0,
        "openFileDescriptors": 0,
        "maxFileDescriptors": 0,
    }
    mock_response = Mock(
        spec=httpx.Response,
        json=lambda: response_data,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.monitoring.infrastructure

    assert result.threadCount == 0
    assert result.cpuLoad == 0.0


@pytest.mark.parametrize(
    "status_code, exception_class, match_message",
    [
        (401, UnauthorisedError, "Request is unauthorised"),
        (403, ForbiddenError, "Request is forbidden"),
        (500, InternalServerError, "Internal server error"),
    ],
)
def test_infrastructure_raises_exceptions_for_error_status_codes(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
    exception_class: type,
    match_message: str,
):
    """Test that infrastructure property raises appropriate exceptions for error responses."""
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
        _ = client.monitoring.infrastructure


@pytest.mark.parametrize(
    "status_code",
    [400, 404, 409, 502, 503],
)
def test_infrastructure_reraises_other_http_errors(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
):
    """Test that infrastructure property re-raises HTTPStatusError for unhandled status codes."""
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
        _ = client.monitoring.infrastructure


def test_infrastructure_raises_response_format_error_for_invalid_json(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that infrastructure property raises ResponseFormatError when JSON parsing fails."""
    mock_response = Mock(spec=httpx.Response)
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(ResponseFormatError, match="Failed to parse response"):
        _ = client.monitoring.infrastructure


@pytest.mark.parametrize(
    "invalid_response",
    [
        {},
        {"heapMemoryUsage": {}},
        {"threadCount": 50},
        {"heapMemoryUsage": {"max": 1000}},
        [],
        "not a dict",
        None,
    ],
)
def test_infrastructure_raises_response_format_error_for_invalid_structure(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    invalid_response,
):
    """Test that infrastructure property raises ResponseFormatError for invalid response structure."""
    mock_response = Mock(
        spec=httpx.Response,
        json=lambda: invalid_response,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(ResponseFormatError, match="Failed to parse response"):
        _ = client.monitoring.infrastructure


def test_infrastructure_handles_large_values(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that infrastructure property handles large integer values correctly."""
    large_value = 2**63 - 1
    response_data = {
        "heapMemoryUsage": {
            "max": large_value,
            "committed": large_value,
            "init": large_value,
            "used": large_value,
        },
        "nonHeapMemoryUsage": {
            "max": large_value,
            "committed": large_value,
            "init": large_value,
            "used": large_value,
        },
        "storageMemory": {
            "dataDirUsed": large_value,
            "workDirUsed": large_value,
            "logsDirUsed": large_value,
            "dataDirFree": large_value,
            "workDirFree": large_value,
            "logsDirFree": large_value,
        },
        "threadCount": large_value,
        "cpuLoad": 1.0,
        "classCount": large_value,
        "gcCount": large_value,
        "openFileDescriptors": large_value,
        "maxFileDescriptors": large_value,
    }
    mock_response = Mock(
        spec=httpx.Response,
        json=lambda: response_data,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.monitoring.infrastructure

    assert result.threadCount == large_value
    assert result.heapMemoryUsage.max == large_value


def test_infrastructure_handles_integer_cpu_load(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that infrastructure property handles integer cpuLoad values (converted to float)."""
    response_data = _make_valid_infrastructure_response()
    response_data["cpuLoad"] = 1
    mock_response = Mock(
        spec=httpx.Response,
        json=lambda: response_data,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.monitoring.infrastructure

    assert result.cpuLoad == 1.0
    assert isinstance(result.cpuLoad, float)
