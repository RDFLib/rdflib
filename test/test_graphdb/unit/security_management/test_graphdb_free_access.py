from __future__ import annotations

from unittest.mock import Mock

import pytest

from rdflib.contrib.graphdb.exceptions import (
    ForbiddenError,
    GraphDBError,
    InternalServerError,
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
    from rdflib.contrib.graphdb.models import FreeAccessSettings


@pytest.mark.parametrize(
    "response_payload",
    [
        {"enabled": True, "authorities": ["ROLE_USER"], "appSettings": {}},
        {"enabled": False, "authorities": [], "appSettings": {"maxAge": 3600}},
    ],
)
def test_free_access_get_details_returns_settings(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    response_payload: dict,
):
    mock_response = Mock(spec=httpx.Response, json=lambda: response_payload)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    settings = client.security.get_free_access_details()

    assert settings == FreeAccessSettings(**response_payload)
    mock_httpx_get.assert_called_once_with(
        "/rest/security/free-access",
        headers={"Accept": "application/json"},
    )


@pytest.mark.parametrize(
    "response_payload",
    [
        {"enabled": "true"},
        {"enabled": True, "authorities": "ROLE_USER"},
        {"enabled": True, "authorities": ["ROLE_USER"], "appSettings": "value"},
    ],
)
def test_free_access_get_details_raises_response_format_error(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    response_payload: dict,
):
    mock_response = Mock(spec=httpx.Response, json=lambda: response_payload)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(ResponseFormatError, match="Failed to parse GraphDB response"):
        _ = client.security.get_free_access_details()


def test_free_access_get_details_raises_response_format_error_on_json_parse_error(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    mock_response = Mock(spec=httpx.Response)
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(ResponseFormatError, match="Failed to parse GraphDB response"):
        _ = client.security.get_free_access_details()


def test_free_access_get_details_raises_internal_server_error(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    mock_response = Mock(spec=httpx.Response, status_code=500, text="Server error")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Internal Server Error",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(InternalServerError):
        _ = client.security.get_free_access_details()


@pytest.mark.parametrize(
    "status_code",
    [400, 401, 403, 404, 409],
)
def test_free_access_get_details_reraises_other_http_errors(
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
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(httpx.HTTPStatusError):
        _ = client.security.get_free_access_details()


def test_free_access_set_details_posts_payload(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    settings = FreeAccessSettings(
        enabled=True, authorities=["ROLE_USER"], appSettings={"maxAge": 3600}
    )
    mock_response = Mock(spec=httpx.Response)
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    client.security.set_free_access_details(settings)

    mock_httpx_post.assert_called_once_with(
        "/rest/security/free-access",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        json=settings.as_dict(),
    )


@pytest.mark.parametrize(
    "response_code, exception_class",
    [
        (200, None),
        (401, UnauthorisedError),
        (403, ForbiddenError),
        (412, PreconditionFailedError),
    ],
)
def test_free_access_set_details_exceptions(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    response_code: int,
    exception_class: type[GraphDBError] | None,
):
    settings = FreeAccessSettings(enabled=True)
    mock_response = Mock(spec=httpx.Response, status_code=response_code, text="Error")
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    if exception_class is not None:
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Mocked exception",
            request=Mock(),
            response=mock_response,
        )
        with pytest.raises(exception_class):
            client.security.set_free_access_details(settings)
    else:
        client.security.set_free_access_details(settings)
