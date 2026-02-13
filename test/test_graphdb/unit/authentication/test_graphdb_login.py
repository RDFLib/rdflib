from __future__ import annotations

from unittest.mock import Mock

import pytest

from rdflib.contrib.graphdb.exceptions import (
    BadRequestError,
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
    from rdflib.contrib.graphdb.models import AuthenticatedUser


def test_login_returns_authenticated_user(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that login returns an AuthenticatedUser with token."""
    response_data = {
        "username": "admin",
        "password": "[CREDENTIALS]",
        "authorities": ["ROLE_USER", "ROLE_ADMIN"],
        "appSettings": {"DEFAULT_INFERENCE": True},
        "external": False,
    }
    mock_response = Mock(spec=httpx.Response)
    mock_response.headers = {"Authorization": "GDB abc123.signature"}
    mock_response.json.return_value = response_data
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    result = client.login("admin", "admin")

    assert isinstance(result, AuthenticatedUser)
    assert result.username == "admin"
    assert result.authorities == ["ROLE_USER", "ROLE_ADMIN"]
    assert result.appSettings == {"DEFAULT_INFERENCE": True}
    assert result.external is False
    assert result.token == "GDB abc123.signature"
    mock_httpx_post.assert_called_once_with(
        "/rest/login",
        json={"username": "admin", "password": "admin"},
    )


def test_login_raises_unauthorised_error_on_401(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that login raises UnauthorisedError on 401 response."""
    mock_response = Mock(spec=httpx.Response, status_code=401, text="Bad credentials")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Unauthorized",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    with pytest.raises(UnauthorisedError, match="Invalid credentials"):
        client.login("admin", "wrongpassword")


def test_login_raises_bad_request_error_on_400(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that login raises BadRequestError on 400 response."""
    mock_response = Mock(spec=httpx.Response, status_code=400, text="Invalid request")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Bad Request",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    with pytest.raises(BadRequestError, match="Invalid request"):
        client.login("admin", "admin")


def test_login_raises_response_format_error_on_missing_authorization_header(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that login raises ResponseFormatError when Authorization header is missing."""
    mock_response = Mock(spec=httpx.Response)
    mock_response.headers = {}
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    with pytest.raises(ResponseFormatError, match="Authorization header missing"):
        client.login("admin", "admin")


def test_login_raises_response_format_error_on_invalid_authorization_header(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that login raises ResponseFormatError when Authorization header has wrong prefix."""
    mock_response = Mock(spec=httpx.Response)
    mock_response.headers = {"Authorization": "Bearer abc123"}
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    with pytest.raises(ResponseFormatError, match="Authorization header missing"):
        client.login("admin", "admin")


def test_login_raises_response_format_error_on_json_parse_error(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that login raises ResponseFormatError when JSON parsing fails."""
    mock_response = Mock(spec=httpx.Response)
    mock_response.headers = {"Authorization": "GDB abc123"}
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    with pytest.raises(ResponseFormatError, match="Failed to parse login response"):
        client.login("admin", "admin")


def test_login_raises_response_format_error_on_invalid_response_data(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that login raises ResponseFormatError when response data is invalid."""
    mock_response = Mock(spec=httpx.Response)
    mock_response.headers = {"Authorization": "GDB abc123"}
    mock_response.json.return_value = {"authorities": ["ROLE_USER"]}  # Missing username
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    with pytest.raises(ResponseFormatError, match="Failed to parse authenticated user"):
        client.login("admin", "admin")


@pytest.mark.parametrize(
    "status_code",
    [403, 404, 409, 500, 503],
)
def test_login_reraises_other_http_errors(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
):
    """Test that login re-raises HTTPStatusError for unhandled status codes."""
    mock_response = Mock(spec=httpx.Response, status_code=status_code, text="Error")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        f"HTTP {status_code}",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    with pytest.raises(httpx.HTTPStatusError):
        client.login("admin", "admin")
