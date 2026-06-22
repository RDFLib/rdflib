from __future__ import annotations

from unittest.mock import Mock

import pytest

from rdflib.contrib.graphdb.exceptions import (
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


def test_delete_config_returns_status_by_node(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    response_data = {
        "http://node1:7200": "Deleted cluster configuration.",
        "http://node2:7200": "Deleted cluster configuration.",
    }
    mock_response = Mock(spec=httpx.Response, json=lambda: response_data)
    mock_httpx_delete = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "delete", mock_httpx_delete)

    result = client.cluster.delete_config()

    assert result == response_data
    mock_httpx_delete.assert_called_once_with(
        "/rest/cluster/config",
        headers={"Accept": "application/json"},
    )
    mock_response.raise_for_status.assert_called_once()


@pytest.mark.parametrize(
    "force, expected",
    [
        (True, "true"),
        (False, "false"),
    ],
)
def test_delete_config_passes_force_query_param(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    force: bool,
    expected: str,
):
    response_data = {"http://node1:7200": "Deleted cluster configuration."}
    mock_response = Mock(spec=httpx.Response, json=lambda: response_data)
    mock_httpx_delete = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "delete", mock_httpx_delete)

    result = client.cluster.delete_config(force=force)

    assert result == response_data
    mock_httpx_delete.assert_called_once_with(
        "/rest/cluster/config",
        headers={"Accept": "application/json"},
        params={"force": expected},
    )


@pytest.mark.parametrize(
    "status_code, exception_class",
    [
        (401, UnauthorisedError),
        (403, ForbiddenError),
        (412, PreconditionFailedError),
    ],
)
def test_delete_config_raises_expected_http_errors(
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
    mock_httpx_delete = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "delete", mock_httpx_delete)

    with pytest.raises(exception_class):
        client.cluster.delete_config()

    mock_httpx_delete.assert_called_once_with(
        "/rest/cluster/config",
        headers={"Accept": "application/json"},
    )


@pytest.mark.parametrize(
    "status_code",
    [400, 404, 409, 500, 503],
)
def test_delete_config_reraises_unexpected_http_errors(
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
    mock_httpx_delete = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "delete", mock_httpx_delete)

    with pytest.raises(httpx.HTTPStatusError):
        client.cluster.delete_config()


def test_delete_config_raises_response_format_error_on_non_object_json(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    mock_response = Mock(spec=httpx.Response, json=lambda: ["not", "a", "dict"])
    mock_httpx_delete = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "delete", mock_httpx_delete)

    with pytest.raises(
        ResponseFormatError, match="Failed to parse cluster deletion response"
    ):
        client.cluster.delete_config()


def test_delete_config_raises_response_format_error_on_non_string_values(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    mock_response = Mock(spec=httpx.Response, json=lambda: {"http://node1:7200": 1})
    mock_httpx_delete = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "delete", mock_httpx_delete)

    with pytest.raises(
        ResponseFormatError, match="Failed to parse cluster deletion response"
    ):
        client.cluster.delete_config()


def test_delete_config_raises_response_format_error_on_json_parse_error(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    mock_response = Mock(spec=httpx.Response)
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_httpx_delete = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "delete", mock_httpx_delete)

    with pytest.raises(
        ResponseFormatError, match="Failed to parse cluster deletion response"
    ):
        client.cluster.delete_config()
