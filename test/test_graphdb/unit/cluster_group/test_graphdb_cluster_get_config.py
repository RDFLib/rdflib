from __future__ import annotations

from unittest.mock import Mock

import pytest

from rdflib.contrib.graphdb.exceptions import (
    InternalServerError,
    NotFoundError,
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
    from rdflib.contrib.graphdb.models import ClusterRequest


def test_get_config_returns_cluster_request(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that get_config returns a ClusterRequest object for a successful response."""
    response_data = {
        "electionMinTimeout": 8000,
        "electionRangeTimeout": 4000,
        "heartbeatInterval": 2000,
        "messageSizeKB": 64,
        "verificationTimeout": 1500,
        "transactionLogMaximumSizeGB": 50,
        "batchUpdateInterval": 10,
        "nodes": ["http://node1:7200", "http://node2:7200"],
    }
    mock_response = Mock(spec=httpx.Response, json=lambda: response_data)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.cluster.get_config()

    assert isinstance(result, ClusterRequest)
    assert result.electionMinTimeout == 8000
    assert result.electionRangeTimeout == 4000
    assert result.heartbeatInterval == 2000
    assert result.messageSizeKB == 64
    assert result.verificationTimeout == 1500
    assert result.transactionLogMaximumSizeGB == 50
    assert result.batchUpdateInterval == 10
    assert result.nodes == ["http://node1:7200", "http://node2:7200"]
    mock_httpx_get.assert_called_once_with(
        "/rest/cluster/config",
        headers={"Accept": "application/json"},
    )


def test_get_config_raises_unauthorised_error_on_401(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that a 401 response raises UnauthorisedError."""
    mock_response = Mock(spec=httpx.Response, status_code=401, text="Unauthorised")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Unauthorised",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(UnauthorisedError, match="Request is unauthorised"):
        client.cluster.get_config()


def test_get_config_raises_not_found_error_on_404(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that a 404 response raises NotFoundError."""
    mock_response = Mock(spec=httpx.Response, status_code=404, text="Not Found")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Not Found",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(NotFoundError, match="Cluster configuration not found"):
        client.cluster.get_config()


def test_get_config_raises_internal_server_error_on_500(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that a 500 response raises InternalServerError."""
    mock_response = Mock(spec=httpx.Response, status_code=500, text="Server error")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Internal Server Error",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(InternalServerError, match="Internal server error"):
        client.cluster.get_config()


@pytest.mark.parametrize(
    "status_code",
    [400, 403, 409, 503],
)
def test_get_config_reraises_other_http_errors(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
):
    """Test that get_config re-raises HTTPStatusError for non-documented status codes."""
    mock_response = Mock(spec=httpx.Response, status_code=status_code, text="Error")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        f"HTTP {status_code}",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(httpx.HTTPStatusError):
        client.cluster.get_config()


@pytest.mark.parametrize(
    "missing_key",
    [
        "electionMinTimeout",
        "electionRangeTimeout",
        "heartbeatInterval",
        "messageSizeKB",
        "verificationTimeout",
        "transactionLogMaximumSizeGB",
        "batchUpdateInterval",
        "nodes",
    ],
)
def test_get_config_raises_response_format_error_on_missing_key(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    missing_key: str,
):
    """Test that get_config raises ResponseFormatError when a required key is missing."""
    response_data = {
        "electionMinTimeout": 8000,
        "electionRangeTimeout": 4000,
        "heartbeatInterval": 2000,
        "messageSizeKB": 64,
        "verificationTimeout": 1500,
        "transactionLogMaximumSizeGB": 50,
        "batchUpdateInterval": 10,
        "nodes": ["http://node1:7200"],
    }
    # Remove the key to test
    del response_data[missing_key]

    mock_response = Mock(spec=httpx.Response, json=lambda: response_data)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(
        ResponseFormatError, match="Failed to parse cluster configuration"
    ):
        client.cluster.get_config()


@pytest.mark.parametrize(
    "invalid_field, invalid_value",
    [
        ("electionMinTimeout", "8000"),
        ("electionRangeTimeout", 4000.5),
        ("heartbeatInterval", None),
        ("messageSizeKB", [64]),
        ("verificationTimeout", True),
        ("transactionLogMaximumSizeGB", {"value": 50}),
        ("batchUpdateInterval", "10"),
        ("nodes", "http://node1:7200"),
        ("nodes", [1, 2, 3]),
    ],
)
def test_get_config_raises_response_format_error_on_invalid_type(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    invalid_field: str,
    invalid_value,
):
    """Test that get_config raises ResponseFormatError when field types are invalid."""
    response_data = {
        "electionMinTimeout": 8000,
        "electionRangeTimeout": 4000,
        "heartbeatInterval": 2000,
        "messageSizeKB": 64,
        "verificationTimeout": 1500,
        "transactionLogMaximumSizeGB": 50,
        "batchUpdateInterval": 10,
        "nodes": ["http://node1:7200"],
    }
    # Set the invalid value
    response_data[invalid_field] = invalid_value

    mock_response = Mock(spec=httpx.Response, json=lambda: response_data)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(
        ResponseFormatError, match="Failed to parse cluster configuration"
    ):
        client.cluster.get_config()


def test_get_config_raises_response_format_error_on_json_parse_error(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that get_config raises ResponseFormatError when JSON parsing fails."""
    mock_response = Mock(spec=httpx.Response)
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(
        ResponseFormatError, match="Failed to parse cluster configuration"
    ):
        client.cluster.get_config()
