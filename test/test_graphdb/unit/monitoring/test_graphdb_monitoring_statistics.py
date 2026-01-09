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
    from rdflib.contrib.graphdb.models import StructureStatistics


def test_structures_returns_structure_statistics(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that structures property returns a StructureStatistics instance."""
    mock_response = Mock(
        spec=httpx.Response,
        json=lambda: {"cacheHit": 100, "cacheMiss": 50},
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.monitoring.structures

    assert isinstance(result, StructureStatistics)
    assert result.cacheHit == 100
    assert result.cacheMiss == 50
    mock_httpx_get.assert_called_once_with(
        "/rest/monitor/structures",
        headers={"Accept": "application/json"},
    )


def test_structures_returns_zero_values(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that structures property handles zero values correctly."""
    mock_response = Mock(
        spec=httpx.Response,
        json=lambda: {"cacheHit": 0, "cacheMiss": 0},
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.monitoring.structures

    assert result.cacheHit == 0
    assert result.cacheMiss == 0


@pytest.mark.parametrize(
    "status_code, exception_class, match_message",
    [
        (401, UnauthorisedError, "Request is unauthorised"),
        (403, ForbiddenError, "Request is forbidden"),
        (500, InternalServerError, "Internal server error"),
        (503, ServiceUnavailableError, "Service is unavailable"),
    ],
)
def test_structures_raises_exceptions_for_error_status_codes(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
    exception_class: type,
    match_message: str,
):
    """Test that structures property raises appropriate exceptions for error responses."""
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
        _ = client.monitoring.structures


@pytest.mark.parametrize(
    "status_code",
    [400, 404, 409, 502],
)
def test_structures_reraises_other_http_errors(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
):
    """Test that structures property re-raises HTTPStatusError for unhandled status codes."""
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
        _ = client.monitoring.structures


def test_structures_raises_response_format_error_for_invalid_json(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that structures property raises ResponseFormatError when JSON parsing fails."""
    mock_response = Mock(spec=httpx.Response)
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(ResponseFormatError, match="Failed to parse response"):
        _ = client.monitoring.structures


@pytest.mark.parametrize(
    "invalid_response",
    [
        {},  # Missing required fields
        {"cacheHit": 100},  # Missing cacheMiss
        {"cacheMiss": 50},  # Missing cacheHit
        {"cacheHit": "100", "cacheMiss": 50},  # Invalid cacheHit type
        {"cacheHit": 100, "cacheMiss": "50"},  # Invalid cacheMiss type
        {"cacheHit": 100.5, "cacheMiss": 50},  # Float instead of int
        {"cacheHit": None, "cacheMiss": 50},  # None value
        [],  # Wrong type entirely
        "not a dict",  # String instead of dict
    ],
)
def test_structures_raises_response_format_error_for_invalid_structure(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    invalid_response,
):
    """Test that structures property raises ResponseFormatError for invalid response structure."""
    mock_response = Mock(
        spec=httpx.Response,
        json=lambda: invalid_response,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(ResponseFormatError, match="Failed to parse response"):
        _ = client.monitoring.structures


def test_structures_handles_large_values(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that structures property handles large integer values correctly."""
    large_value = 2**63 - 1  # Max 64-bit signed integer
    mock_response = Mock(
        spec=httpx.Response,
        json=lambda: {"cacheHit": large_value, "cacheMiss": large_value},
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.monitoring.structures

    assert result.cacheHit == large_value
    assert result.cacheMiss == large_value
