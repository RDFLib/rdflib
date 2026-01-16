from __future__ import annotations

from unittest.mock import Mock

import pytest

from rdflib.contrib.graphdb.exceptions import (
    BadRequestError,
    ForbiddenError,
    PreconditionFailedError,
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


def test_update_config_patches_payload_and_returns_cluster_request(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
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
    mock_httpx_patch = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "patch", mock_httpx_patch)

    result = client.cluster.update_config(
        election_min_timeout=8000,
        election_range_timeout=4000,
        heartbeat_interval=2000,
        message_size_kb=64,
        verification_timeout=1500,
        transaction_log_maximum_size_gb=50,
        batch_update_interval=10,
    )

    assert isinstance(result, ClusterRequest)
    assert result.electionMinTimeout == 8000
    assert result.electionRangeTimeout == 4000
    assert result.heartbeatInterval == 2000
    assert result.messageSizeKB == 64
    assert result.verificationTimeout == 1500
    assert result.transactionLogMaximumSizeGB == 50
    assert result.batchUpdateInterval == 10
    assert result.nodes == ["http://node1:7200", "http://node2:7200"]
    mock_httpx_patch.assert_called_once_with(
        "/rest/cluster/config",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        json={
            "electionMinTimeout": 8000,
            "electionRangeTimeout": 4000,
            "heartbeatInterval": 2000,
            "messageSizeKB": 64,
            "verificationTimeout": 1500,
            "transactionLogMaximumSizeGB": 50,
            "batchUpdateInterval": 10,
        },
    )


def test_update_config_omits_optional_fields_when_none(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
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
    mock_httpx_patch = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "patch", mock_httpx_patch)

    result = client.cluster.update_config()

    assert isinstance(result, ClusterRequest)
    mock_httpx_patch.assert_called_once_with(
        "/rest/cluster/config",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        json={},
    )


@pytest.mark.parametrize(
    "status_code, exception_class",
    [
        (400, BadRequestError),
        (401, UnauthorisedError),
        (403, ForbiddenError),
        (412, PreconditionFailedError),
    ],
)
def test_update_config_raises_expected_http_errors(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
    exception_class: type[Exception],
):
    mock_response = Mock(
        spec=httpx.Response, status_code=status_code, text="Error message"
    )
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        f"HTTP {status_code}",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_patch = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "patch", mock_httpx_patch)

    with pytest.raises(exception_class):
        client.cluster.update_config(election_min_timeout=8000)


@pytest.mark.parametrize("status_code", [404, 409, 500, 503])
def test_update_config_reraises_unexpected_http_errors(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
):
    mock_response = Mock(spec=httpx.Response, status_code=status_code, text="Error")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        f"HTTP {status_code}",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_patch = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "patch", mock_httpx_patch)

    with pytest.raises(httpx.HTTPStatusError):
        client.cluster.update_config(election_min_timeout=8000)


@pytest.mark.parametrize(
    "field,value",
    [
        ("election_min_timeout", "8000"),
        ("election_range_timeout", 4000.5),
        ("heartbeat_interval", True),
        ("message_size_kb", "64"),
        ("verification_timeout", {"value": 1500}),
        ("transaction_log_maximum_size_gb", [50]),
        ("batch_update_interval", [10]),
    ],
)
def test_update_config_validates_int_fields_when_provided(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    value,
):
    mock_httpx_patch = Mock()
    monkeypatch.setattr(httpx.Client, "patch", mock_httpx_patch)

    with pytest.raises(TypeError, match=f"{field} must be an int if provided"):
        client.cluster.update_config(**{field: value})

    mock_httpx_patch.assert_not_called()


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
def test_update_config_raises_response_format_error_on_missing_key(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    missing_key: str,
):
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
    del response_data[missing_key]

    mock_response = Mock(spec=httpx.Response, json=lambda: response_data)
    mock_httpx_patch = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "patch", mock_httpx_patch)

    with pytest.raises(
        ResponseFormatError, match="Failed to parse updated cluster configuration"
    ):
        client.cluster.update_config(election_min_timeout=8000)


def test_update_config_raises_response_format_error_on_json_parse_error(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    mock_response = Mock(spec=httpx.Response)
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_httpx_patch = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "patch", mock_httpx_patch)

    with pytest.raises(
        ResponseFormatError, match="Failed to parse updated cluster configuration"
    ):
        client.cluster.update_config(election_min_timeout=8000)
