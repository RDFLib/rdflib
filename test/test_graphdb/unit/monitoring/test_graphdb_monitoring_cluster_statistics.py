from __future__ import annotations

from unittest.mock import Mock

import pytest

from rdflib.contrib.graphdb.exceptions import (
    ForbiddenError,
    InternalServerError,
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


def test_cluster_returns_prometheus_metrics(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that cluster method returns Prometheus-style metrics as a string."""
    prometheus_metrics = """# HELP graphdb_cluster_node_count Number of nodes in the cluster
# TYPE graphdb_cluster_node_count gauge
graphdb_cluster_node_count 3
# HELP graphdb_cluster_healthy Cluster health status
# TYPE graphdb_cluster_healthy gauge
graphdb_cluster_healthy 1
"""
    mock_response = Mock(
        spec=httpx.Response,
        text=prometheus_metrics,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.monitoring.cluster()

    assert isinstance(result, str)
    assert result == prometheus_metrics
    mock_httpx_get.assert_called_once_with(
        "/rest/monitor/cluster",
        headers={"Accept": "text/plain"},
    )


def test_cluster_returns_empty_string(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that cluster method handles empty response correctly."""
    mock_response = Mock(
        spec=httpx.Response,
        text="",
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.monitoring.cluster()

    assert result == ""


@pytest.mark.parametrize(
    "status_code, exception_class, match_message",
    [
        (401, UnauthorisedError, "Request is unauthorised"),
        (403, ForbiddenError, "Request is forbidden"),
        (500, InternalServerError, "Internal server error"),
        (503, ServiceUnavailableError, "Service is unavailable"),
    ],
)
def test_cluster_raises_exceptions_for_error_status_codes(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
    exception_class: type,
    match_message: str,
):
    """Test that cluster method raises appropriate exceptions for error responses."""
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
        client.monitoring.cluster()


@pytest.mark.parametrize(
    "status_code",
    [400, 404, 409, 502],
)
def test_cluster_reraises_other_http_errors(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
):
    """Test that cluster method re-raises HTTPStatusError for unhandled status codes."""
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
        client.monitoring.cluster()


def test_cluster_handles_multiline_metrics(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that cluster method handles multi-line Prometheus metrics correctly."""
    metrics = "\n".join(
        [
            "# HELP graphdb_cluster_node_count Number of nodes",
            "# TYPE graphdb_cluster_node_count gauge",
            "graphdb_cluster_node_count 5",
            "# HELP graphdb_cluster_leader_id Current leader node ID",
            "# TYPE graphdb_cluster_leader_id gauge",
            'graphdb_cluster_leader_id{node="node1"} 1',
            "# HELP graphdb_cluster_replica_count Number of replicas",
            "# TYPE graphdb_cluster_replica_count gauge",
            "graphdb_cluster_replica_count 2",
        ]
    )
    mock_response = Mock(
        spec=httpx.Response,
        text=metrics,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.monitoring.cluster()

    assert result == metrics
    assert "graphdb_cluster_node_count 5" in result
    assert "graphdb_cluster_replica_count 2" in result
