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
    from rdflib.contrib.graphdb.models import RepositoryStatistics


def test_get_repo_stats_returns_repository_statistics(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that get_repo_stats returns a RepositoryStatistics instance."""
    mock_response = Mock(
        spec=httpx.Response,
        json=lambda: {
            "queries": {"slow": 10, "suboptimal": 5},
            "entityPool": {"epoolReads": 100, "epoolWrites": 50, "epoolSize": 1000},
            "activeTransactions": 2,
            "openConnections": 3,
        },
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.monitoring.get_repo_stats("test-repo")

    assert isinstance(result, RepositoryStatistics)
    assert result.queries.slow == 10
    assert result.queries.suboptimal == 5
    assert result.entityPool.epoolReads == 100
    assert result.entityPool.epoolWrites == 50
    assert result.entityPool.epoolSize == 1000
    assert result.activeTransactions == 2
    assert result.openConnections == 3
    mock_httpx_get.assert_called_once_with(
        "/rest/monitor/repository/test-repo",
        headers={"Accept": "application/json"},
    )


def test_get_repo_stats_returns_zero_values(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that get_repo_stats handles zero values correctly."""
    mock_response = Mock(
        spec=httpx.Response,
        json=lambda: {
            "queries": {"slow": 0, "suboptimal": 0},
            "entityPool": {"epoolReads": 0, "epoolWrites": 0, "epoolSize": 0},
            "activeTransactions": 0,
            "openConnections": 0,
        },
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.monitoring.get_repo_stats("test-repo")

    assert result.queries.slow == 0
    assert result.queries.suboptimal == 0
    assert result.entityPool.epoolReads == 0
    assert result.entityPool.epoolWrites == 0
    assert result.entityPool.epoolSize == 0
    assert result.activeTransactions == 0
    assert result.openConnections == 0


@pytest.mark.parametrize(
    "status_code, exception_class, match_message",
    [
        (401, UnauthorisedError, "Request is unauthorised"),
        (403, ForbiddenError, "Request is forbidden"),
        (500, InternalServerError, "Internal server error"),
    ],
)
def test_get_repo_stats_raises_exceptions_for_error_status_codes(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
    exception_class: type,
    match_message: str,
):
    """Test that get_repo_stats raises appropriate exceptions for error responses."""
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
        client.monitoring.get_repo_stats("test-repo")


@pytest.mark.parametrize(
    "status_code",
    [400, 404, 409, 502, 503],
)
def test_get_repo_stats_reraises_other_http_errors(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
):
    """Test that get_repo_stats re-raises HTTPStatusError for unhandled status codes."""
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
        client.monitoring.get_repo_stats("test-repo")


def test_get_repo_stats_raises_response_format_error_for_invalid_json(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that get_repo_stats raises ResponseFormatError when JSON parsing fails."""
    mock_response = Mock(spec=httpx.Response)
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(ResponseFormatError, match="Failed to parse response"):
        client.monitoring.get_repo_stats("test-repo")


@pytest.mark.parametrize(
    "invalid_response",
    [
        {},  # Missing required fields
        {"queries": {"slow": 10, "suboptimal": 5}},  # Missing entityPool and others
        {
            "entityPool": {"epoolReads": 0, "epoolWrites": 0, "epoolSize": 0}
        },  # Missing queries and others
        {  # Invalid queries type
            "queries": "invalid",
            "entityPool": {"epoolReads": 0, "epoolWrites": 0, "epoolSize": 0},
            "activeTransactions": 0,
            "openConnections": 0,
        },
        {  # Invalid entityPool type
            "queries": {"slow": 0, "suboptimal": 0},
            "entityPool": "invalid",
            "activeTransactions": 0,
            "openConnections": 0,
        },
        {  # Invalid activeTransactions type
            "queries": {"slow": 0, "suboptimal": 0},
            "entityPool": {"epoolReads": 0, "epoolWrites": 0, "epoolSize": 0},
            "activeTransactions": "invalid",
            "openConnections": 0,
        },
        {  # Invalid openConnections type
            "queries": {"slow": 0, "suboptimal": 0},
            "entityPool": {"epoolReads": 0, "epoolWrites": 0, "epoolSize": 0},
            "activeTransactions": 0,
            "openConnections": "invalid",
        },
        {  # Invalid nested queries.slow type
            "queries": {"slow": "invalid", "suboptimal": 0},
            "entityPool": {"epoolReads": 0, "epoolWrites": 0, "epoolSize": 0},
            "activeTransactions": 0,
            "openConnections": 0,
        },
        {  # Invalid nested entityPool.epoolReads type
            "queries": {"slow": 0, "suboptimal": 0},
            "entityPool": {"epoolReads": "invalid", "epoolWrites": 0, "epoolSize": 0},
            "activeTransactions": 0,
            "openConnections": 0,
        },
        [],  # Wrong type entirely
        "not a dict",  # String instead of dict
    ],
)
def test_get_repo_stats_raises_response_format_error_for_invalid_structure(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    invalid_response,
):
    """Test that get_repo_stats raises ResponseFormatError for invalid response structure."""
    mock_response = Mock(
        spec=httpx.Response,
        json=lambda: invalid_response,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(ResponseFormatError, match="Failed to parse response"):
        client.monitoring.get_repo_stats("test-repo")


def test_get_repo_stats_handles_large_values(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that get_repo_stats handles large integer values correctly."""
    large_value = 2**63 - 1  # Max 64-bit signed integer
    mock_response = Mock(
        spec=httpx.Response,
        json=lambda: {
            "queries": {"slow": large_value, "suboptimal": large_value},
            "entityPool": {
                "epoolReads": large_value,
                "epoolWrites": large_value,
                "epoolSize": large_value,
            },
            "activeTransactions": large_value,
            "openConnections": large_value,
        },
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.monitoring.get_repo_stats("test-repo")

    assert result.queries.slow == large_value
    assert result.queries.suboptimal == large_value
    assert result.entityPool.epoolReads == large_value
    assert result.entityPool.epoolWrites == large_value
    assert result.entityPool.epoolSize == large_value
    assert result.activeTransactions == large_value
    assert result.openConnections == large_value


def test_get_repo_stats_uses_correct_repository_id_in_url(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that get_repo_stats uses the correct repository ID in the URL."""
    mock_response = Mock(
        spec=httpx.Response,
        json=lambda: {
            "queries": {"slow": 0, "suboptimal": 0},
            "entityPool": {"epoolReads": 0, "epoolWrites": 0, "epoolSize": 0},
            "activeTransactions": 0,
            "openConnections": 0,
        },
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    client.monitoring.get_repo_stats("my-custom-repo")

    mock_httpx_get.assert_called_once_with(
        "/rest/monitor/repository/my-custom-repo",
        headers={"Accept": "application/json"},
    )
