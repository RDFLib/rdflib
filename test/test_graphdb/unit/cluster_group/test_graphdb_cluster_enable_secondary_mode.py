from __future__ import annotations

from unittest.mock import Mock

import pytest

from rdflib.contrib.graphdb.exceptions import (
    BadRequestError,
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


def test_enable_secondary_mode_posts_payload_and_returns_none(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    mock_response = Mock(spec=httpx.Response, status_code=200)
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    client.cluster.enable_secondary_mode(primary_node="rpc://primary:7300", tag="tag-1")

    mock_httpx_post.assert_called_once_with(
        "/rest/cluster/config/secondary-mode",
        json={"primaryNode": "rpc://primary:7300", "tag": "tag-1"},
    )
    mock_response.raise_for_status.assert_called_once()


@pytest.mark.parametrize(
    "status_code, exception_class",
    [
        (400, BadRequestError),
        (401, UnauthorisedError),
        (403, ForbiddenError),
        (412, PreconditionFailedError),
    ],
)
def test_enable_secondary_mode_raises_expected_http_errors(
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
        client.cluster.enable_secondary_mode(primary_node="rpc://primary:7300", tag="t")


@pytest.mark.parametrize("status_code", [404, 409, 500, 503])
def test_enable_secondary_mode_reraises_unexpected_http_errors(
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
        client.cluster.enable_secondary_mode(primary_node="rpc://primary:7300", tag="t")


@pytest.mark.parametrize("primary_node", [123, None, ["rpc://primary:7300"]])
def test_enable_secondary_mode_validates_primary_node_type(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    primary_node,
):
    mock_httpx_post = Mock()
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    with pytest.raises(TypeError, match="primary_node must be a string"):
        client.cluster.enable_secondary_mode(primary_node=primary_node, tag="t")

    mock_httpx_post.assert_not_called()


def test_enable_secondary_mode_rejects_empty_primary_node(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    mock_httpx_post = Mock()
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    with pytest.raises(ValueError, match="primary_node must be a non-empty string"):
        client.cluster.enable_secondary_mode(primary_node="", tag="t")

    mock_httpx_post.assert_not_called()


@pytest.mark.parametrize("tag", [123, None, ["some-tag"]])
def test_enable_secondary_mode_validates_tag_type(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    tag,
):
    mock_httpx_post = Mock()
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    with pytest.raises(TypeError, match="tag must be a string"):
        client.cluster.enable_secondary_mode(primary_node="rpc://primary:7300", tag=tag)

    mock_httpx_post.assert_not_called()


def test_enable_secondary_mode_rejects_empty_tag(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    mock_httpx_post = Mock()
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    with pytest.raises(ValueError, match="tag must be a non-empty string"):
        client.cluster.enable_secondary_mode(primary_node="rpc://primary:7300", tag="")

    mock_httpx_post.assert_not_called()
