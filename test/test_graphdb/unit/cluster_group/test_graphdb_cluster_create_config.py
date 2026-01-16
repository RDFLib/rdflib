from __future__ import annotations

from unittest.mock import Mock

import pytest

from rdflib.contrib.graphdb.exceptions import (
    BadRequestError,
    ConflictError,
    ForbiddenError,
    PreconditionFailedError,
    UnauthorisedError,
)
from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    import httpx

    from rdflib.contrib.graphdb.client import GraphDBClient


def test_create_config_posts_payload_and_returns_none(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    mock_response = Mock(spec=httpx.Response, status_code=201)
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    result = client.cluster.create_config(
        nodes=["http://node1:7200", "http://node2:7200"],
        election_min_timeout=8000,
        election_range_timeout=4000,
        heartbeat_interval=2000,
        message_size_kb=64,
        verification_timeout=1500,
        transaction_log_maximum_size_gb=50,
        batch_update_interval=10,
    )

    assert result is None
    mock_httpx_post.assert_called_once_with(
        "/rest/cluster/config",
        headers={"Content-Type": "application/json"},
        json={
            "nodes": ["http://node1:7200", "http://node2:7200"],
            "electionMinTimeout": 8000,
            "electionRangeTimeout": 4000,
            "heartbeatInterval": 2000,
            "messageSizeKB": 64,
            "verificationTimeout": 1500,
            "transactionLogMaximumSizeGB": 50,
            "batchUpdateInterval": 10,
        },
    )
    mock_response.raise_for_status.assert_called_once()


def test_create_config_omits_optional_fields_when_none(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    mock_response = Mock(spec=httpx.Response, status_code=201)
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    result = client.cluster.create_config(nodes=["http://node1:7200"])

    assert result is None
    mock_httpx_post.assert_called_once_with(
        "/rest/cluster/config",
        headers={"Content-Type": "application/json"},
        json={"nodes": ["http://node1:7200"]},
    )
    mock_response.raise_for_status.assert_called_once()


@pytest.mark.parametrize(
    "status_code, exception_class",
    [
        (400, BadRequestError),
        (401, UnauthorisedError),
        (403, ForbiddenError),
        (409, ConflictError),
        (412, PreconditionFailedError),
    ],
)
def test_create_config_raises_expected_http_errors(
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
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    with pytest.raises(exception_class):
        client.cluster.create_config(nodes=["http://node1:7200"])


@pytest.mark.parametrize("status_code", [404, 500, 503])
def test_create_config_reraises_unexpected_http_errors(
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
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    with pytest.raises(httpx.HTTPStatusError):
        client.cluster.create_config(nodes=["http://node1:7200"])


@pytest.mark.parametrize(
    "nodes",
    ["http://node1:7200", [1, 2, 3]],
)
def test_create_config_validates_nodes_type(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    nodes,
):
    mock_httpx_post = Mock()
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    with pytest.raises(TypeError, match="nodes must be a list\\[str\\]"):
        client.cluster.create_config(nodes=nodes)  # type: ignore[arg-type]

    mock_httpx_post.assert_not_called()


@pytest.mark.parametrize(
    "field,value",
    [
        ("election_min_timeout", "8000"),
        ("election_range_timeout", 4000.5),
        ("heartbeat_interval", True),
        ("message_size_kb", "64"),
        ("verification_timeout", {"value": 1500}),
        ("batch_update_interval", [10]),
    ],
)
def test_create_config_validates_int_fields_when_provided(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    value,
):
    mock_httpx_post = Mock()
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    with pytest.raises(TypeError, match=f"{field} must be an int if provided"):
        client.cluster.create_config(nodes=["http://node1:7200"], **{field: value})

    mock_httpx_post.assert_not_called()
