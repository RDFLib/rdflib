from __future__ import annotations

from unittest.mock import Mock

import pytest

from rdflib.contrib.graphdb.exceptions import (
    ForbiddenError,
    GraphDBError,
    InternalServerError,
    PreconditionFailedError,
    UnauthorisedError,
)
from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    import httpx

    from rdflib.contrib.graphdb.client import (
        GraphDBClient,
    )


@pytest.mark.parametrize(
    "response_value, expected",
    [
        (True, True),
        (False, False),
    ],
)
def test_security_enabled_getter_returns_boolean(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    response_value: bool,
    expected: bool,
):
    """Test that the enabled getter correctly returns the boolean value from the API."""
    mock_response = Mock(spec=httpx.Response, json=lambda: response_value)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.security.enabled

    assert result == expected
    mock_httpx_get.assert_called_once_with(
        "/rest/security",
        headers={"Accept": "application/json"},
    )


def test_security_enabled_getter_raises_internal_server_error(
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

    with pytest.raises(InternalServerError):
        _ = client.security.enabled


@pytest.mark.parametrize(
    "value",
    [True, False],
)
def test_security_enabled_setter_sends_boolean(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    value: bool,
):
    """Test that the enabled setter correctly sends the boolean value to the API."""
    mock_response = Mock(spec=httpx.Response)
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    client.security.enabled = value

    mock_httpx_post.assert_called_once_with(
        "/rest/security",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        json=value,
    )


@pytest.mark.parametrize(
    "invalid_value",
    [
        "true",
        "false",
        1,
        0,
        None,
        [],
        {},
    ],
)
def test_security_enabled_setter_raises_type_error_for_non_boolean(
    client: GraphDBClient,
    invalid_value,
):
    """Test that the setter raises TypeError when value is not a boolean."""
    with pytest.raises(TypeError, match="Value must be a boolean"):
        client.security.enabled = invalid_value


@pytest.mark.parametrize(
    "response_code, exception_class",
    [
        (200, None),
        (401, UnauthorisedError),
        (403, ForbiddenError),
        (412, PreconditionFailedError),
    ],
)
def test_security_enabled_setter_exceptions(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    response_code: int,
    exception_class: type[GraphDBError] | None,
):
    """Test that the setter raises appropriate exceptions for error responses."""
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
            client.security.enabled = True
    else:
        # Should not raise for success codes
        client.security.enabled = True
