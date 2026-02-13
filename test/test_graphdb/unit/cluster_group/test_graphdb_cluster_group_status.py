from __future__ import annotations

from unittest.mock import Mock

import pytest

from rdflib.contrib.graphdb.exceptions import (
    BadRequestError,
    InternalServerError,
    NotFoundError,
    ResponseFormatError,
)
from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    import httpx

    from rdflib.contrib.graphdb.client import GraphDBClient
    from rdflib.contrib.graphdb.models import NodeStatus


def test_group_status_returns_list_of_node_status(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that group_status returns a list of NodeStatus objects for a successful response."""
    response_data = [
        {
            "address": "node1:7200",
            "nodeState": "LEADER",
            "term": 5,
            "syncStatus": {"node2:7200": "IN_SYNC"},
            "lastLogTerm": 5,
            "lastLogIndex": 100,
            "endpoint": "http://node1:7200",
            "recoveryStatus": {},
            "topologyStatus": {
                "state": "STANDALONE",
                "primaryTags": {},
            },
            "clusterEnabled": True,
        },
        {
            "address": "node2:7200",
            "nodeState": "FOLLOWER",
            "term": 5,
            "syncStatus": {"node1:7200": "IN_SYNC"},
            "lastLogTerm": 5,
            "lastLogIndex": 99,
            "endpoint": "http://node2:7200",
            "recoveryStatus": {},
            "topologyStatus": {
                "state": "STANDALONE",
                "primaryTags": {},
            },
            "clusterEnabled": True,
        },
    ]
    mock_response = Mock(spec=httpx.Response, json=lambda: response_data)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.cluster.group_status()

    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(node, NodeStatus) for node in result)
    assert result[0].address == "node1:7200"
    assert result[0].nodeState == "LEADER"
    assert result[0].term == 5
    assert result[1].address == "node2:7200"
    assert result[1].nodeState == "FOLLOWER"
    assert result[1].term == 5
    mock_httpx_get.assert_called_once_with(
        "/rest/cluster/group/status",
        headers={"Accept": "application/json"},
    )


def test_group_status_returns_empty_list_for_empty_response(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that group_status returns an empty list when the response is empty."""
    response_data: list[dict] = []
    mock_response = Mock(spec=httpx.Response, json=lambda: response_data)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.cluster.group_status()

    assert isinstance(result, list)
    assert len(result) == 0


def test_group_status_raises_bad_request_error_on_400(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that a 400 response raises BadRequestError."""
    mock_response = Mock(spec=httpx.Response, status_code=400, text="Bad Request")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Bad Request",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(BadRequestError, match="Invalid request"):
        client.cluster.group_status()


def test_group_status_raises_not_found_error_on_404(
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

    with pytest.raises(NotFoundError, match="Group status not found"):
        client.cluster.group_status()


def test_group_status_raises_internal_server_error_on_500(
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
        client.cluster.group_status()


@pytest.mark.parametrize(
    "status_code",
    [401, 403, 409, 503],
)
def test_group_status_reraises_other_http_errors(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
):
    """Test that group_status re-raises HTTPStatusError for non-documented status codes."""
    mock_response = Mock(spec=httpx.Response, status_code=status_code, text="Error")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        f"HTTP {status_code}",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(httpx.HTTPStatusError):
        client.cluster.group_status()


@pytest.mark.parametrize(
    "missing_key",
    [
        "address",
        "nodeState",
        "term",
        "syncStatus",
        "lastLogTerm",
        "lastLogIndex",
        "endpoint",
    ],
)
def test_group_status_raises_response_format_error_on_missing_key(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    missing_key: str,
):
    """Test that group_status raises ResponseFormatError when a required key is missing."""
    node_data = {
        "address": "node1:7200",
        "nodeState": "LEADER",
        "term": 5,
        "syncStatus": {"node2:7200": "IN_SYNC"},
        "lastLogTerm": 5,
        "lastLogIndex": 100,
        "endpoint": "http://node1:7200",
        "recoveryStatus": {},
        "topologyStatus": None,
        "clusterEnabled": True,
    }
    # Remove the key to test
    del node_data[missing_key]

    response_data = [node_data]
    mock_response = Mock(spec=httpx.Response, json=lambda: response_data)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(ResponseFormatError, match="Failed to parse group status"):
        client.cluster.group_status()


@pytest.mark.parametrize(
    "invalid_field, invalid_value",
    [
        ("address", 123),
        ("nodeState", None),
        ("term", "5"),
        ("term", 5.5),
        ("syncStatus", "IN_SYNC"),
        ("syncStatus", []),
        ("lastLogTerm", "5"),
        ("lastLogIndex", 100.5),
        ("endpoint", ["http://node1:7200"]),
        ("clusterEnabled", "true"),
    ],
)
def test_group_status_raises_response_format_error_on_invalid_type(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    invalid_field: str,
    invalid_value,
):
    """Test that group_status raises ResponseFormatError when field types are invalid."""
    node_data = {
        "address": "node1:7200",
        "nodeState": "LEADER",
        "term": 5,
        "syncStatus": {"node2:7200": "IN_SYNC"},
        "lastLogTerm": 5,
        "lastLogIndex": 100,
        "endpoint": "http://node1:7200",
        "recoveryStatus": {},
        "topologyStatus": None,
        "clusterEnabled": True,
    }
    # Set the invalid value
    node_data[invalid_field] = invalid_value

    response_data = [node_data]
    mock_response = Mock(spec=httpx.Response, json=lambda: response_data)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(ResponseFormatError, match="Failed to parse group status"):
        client.cluster.group_status()


def test_group_status_raises_response_format_error_on_json_parse_error(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that group_status raises ResponseFormatError when JSON parsing fails."""
    mock_response = Mock(spec=httpx.Response)
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(ResponseFormatError, match="Failed to parse group status"):
        client.cluster.group_status()


def test_group_status_raises_response_format_error_on_non_list_response(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that group_status raises ResponseFormatError when response is not a list."""
    response_data = {
        "address": "node1:7200",
        "nodeState": "LEADER",
        "term": 5,
    }  # Should be a list, not a dict
    mock_response = Mock(spec=httpx.Response, json=lambda: response_data)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(ResponseFormatError, match="Failed to parse group status"):
        client.cluster.group_status()


def test_group_status_handles_partial_node_status_data(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that group_status correctly handles NodeStatus with optional fields missing."""
    response_data = [
        {
            "address": "node1:7200",
            "nodeState": "LEADER",
            "term": 5,
            "syncStatus": {},
            "lastLogTerm": 5,
            "lastLogIndex": 100,
            "endpoint": "http://node1:7200",
            "recoveryStatus": {},
            # topologyStatus is optional
            # clusterEnabled is optional
        }
    ]
    mock_response = Mock(spec=httpx.Response, json=lambda: response_data)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.cluster.group_status()

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].address == "node1:7200"
    assert result[0].topologyStatus is None
    assert result[0].clusterEnabled is None
