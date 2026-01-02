from __future__ import annotations

from unittest.mock import Mock

import pytest

from rdflib.contrib.graphdb.exceptions import (
    ForbiddenError,
    GraphDBError,
    InternalServerError,
    NotFoundError,
    PreconditionFailedError,
    ResponseFormatError,
    UnauthorisedError,
)
from rdflib.contrib.graphdb.models import User
from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    import httpx

    from rdflib.contrib.graphdb.client import (
        GraphDBClient,
    )


def _make_user_dict(
    username: str = "admin",
    password: str = "",
    date_created: int = 1736234567890,
    granted_authorities: list[str] | None = None,
    app_settings: dict | None = None,
    gpt_threads: list | None = None,
) -> dict:
    """Helper to create a user dict matching GraphDB API response format."""
    return {
        "username": username,
        "password": password,
        "dateCreated": date_created,
        "grantedAuthorities": (
            granted_authorities if granted_authorities is not None else ["ROLE_ADMIN"]
        ),
        "appSettings": app_settings if app_settings is not None else {},
        "gptThreads": gpt_threads if gpt_threads is not None else [],
    }


def test_get_users_returns_list_of_users(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that get_users returns a list of User objects."""
    users_data = [
        _make_user_dict("admin", "", 1736234567890, ["ROLE_ADMIN"]),
        _make_user_dict("user1", "", 1736234567891, ["ROLE_USER"]),
    ]
    mock_response = Mock(spec=httpx.Response, json=lambda: users_data)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.users.list()

    assert len(result) == 2
    assert all(isinstance(user, User) for user in result)
    assert result[0].username == "admin"
    assert result[1].username == "user1"
    mock_httpx_get.assert_called_once_with(
        "/rest/security/users",
        headers={"Accept": "application/json"},
    )


def test_get_users_returns_empty_list(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that get_users returns an empty list when no users exist."""
    mock_response = Mock(spec=httpx.Response, json=lambda: [])
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.users.list()

    assert result == []


def test_get_users_parses_user_fields_correctly(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that get_users correctly parses all User fields from the response."""
    users_data = [
        {
            "username": "testuser",
            "password": "hashedpwd",
            "dateCreated": 1736234567890,
            "grantedAuthorities": ["ROLE_USER", "READ_REPO_test"],
            "appSettings": {"theme": "dark", "language": "en"},
            "gptThreads": ["thread1", "thread2"],
        }
    ]
    mock_response = Mock(spec=httpx.Response, json=lambda: users_data)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.users.list()

    assert len(result) == 1
    user = result[0]
    assert user.username == "testuser"
    assert user.password == "hashedpwd"
    assert user.dateCreated == 1736234567890
    assert user.grantedAuthorities == ["ROLE_USER", "READ_REPO_test"]
    assert user.appSettings == {"theme": "dark", "language": "en"}
    assert user.gptThreads == ["thread1", "thread2"]


def test_get_users_handles_null_optional_fields(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that get_users handles null values for optional fields."""
    users_data = [
        {
            "username": "testuser",
            "password": "",
            "dateCreated": 1736234567890,
            "grantedAuthorities": None,
            "appSettings": None,
            "gptThreads": None,
        }
    ]
    mock_response = Mock(spec=httpx.Response, json=lambda: users_data)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.users.list()

    assert len(result) == 1
    user = result[0]
    # User.__post_init__ normalizes None to empty collections
    assert user.grantedAuthorities == []
    assert user.appSettings == {}
    assert user.gptThreads == []


def test_get_users_raises_response_format_error_on_json_parse_error(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that get_users raises ResponseFormatError when JSON parsing fails."""
    mock_response = Mock(spec=httpx.Response)
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(ResponseFormatError, match="Failed to parse GraphDB response"):
        client.users.list()


def test_get_users_raises_response_format_error_on_invalid_user_data(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that get_users raises ResponseFormatError when user data is invalid."""
    # Missing required field 'username'
    users_data = [
        {
            "password": "",
            "dateCreated": 1736234567890,
        }
    ]
    mock_response = Mock(spec=httpx.Response, json=lambda: users_data)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(ResponseFormatError, match="Failed to parse GraphDB response"):
        client.users.list()


@pytest.mark.parametrize(
    "status_code, exception_class",
    [
        (401, UnauthorisedError),
        (403, ForbiddenError),
        (412, PreconditionFailedError),
        (500, InternalServerError),
    ],
)
def test_get_users_raises_appropriate_exceptions(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
    exception_class: type[GraphDBError],
):
    """Test that get_users raises appropriate exceptions for error responses."""
    mock_response = Mock(spec=httpx.Response, status_code=status_code, text="Error")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        f"HTTP {status_code}",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(exception_class):
        client.users.list()


@pytest.mark.parametrize(
    "status_code",
    [400, 404, 409, 502, 503],
)
def test_get_users_reraises_other_http_errors(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
):
    """Test that get_users re-raises HTTPStatusError for unhandled status codes."""
    mock_response = Mock(spec=httpx.Response, status_code=status_code, text="Error")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        f"HTTP {status_code}",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(httpx.HTTPStatusError):
        client.users.list()


def test_get_users_raises_unauthorised_error_message(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that UnauthorisedError has the correct message."""
    mock_response = Mock(spec=httpx.Response, status_code=401, text="Unauthorized")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "HTTP 401",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(UnauthorisedError, match="Request is unauthorised"):
        client.users.list()


def test_get_users_raises_forbidden_error_message(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that ForbiddenError has the correct message."""
    mock_response = Mock(spec=httpx.Response, status_code=403, text="Forbidden")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "HTTP 403",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(ForbiddenError, match="Request is forbidden"):
        client.users.list()


def test_get_users_internal_server_error_includes_response_text(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that InternalServerError includes the response text in the message."""
    error_text = "Database connection failed"
    mock_response = Mock(spec=httpx.Response, status_code=500, text=error_text)
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "HTTP 500",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(InternalServerError, match=error_text):
        client.users.list()


def test_get_user_returns_user(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that get returns a User object."""
    user_data = _make_user_dict("admin", "", 1736234567890, ["ROLE_ADMIN"])
    mock_response = Mock(spec=httpx.Response, json=lambda: user_data)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.users.get("admin")

    assert isinstance(result, User)
    assert result.username == "admin"
    mock_httpx_get.assert_called_once_with(
        "/rest/security/users/admin",
        headers={"Accept": "application/json"},
    )


def test_get_user_parses_all_fields_correctly(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that get correctly parses all User fields from the response."""
    user_data = {
        "username": "testuser",
        "password": "hashedpwd",
        "dateCreated": 1736234567890,
        "grantedAuthorities": ["ROLE_USER", "READ_REPO_test"],
        "appSettings": {"theme": "dark", "language": "en"},
        "gptThreads": ["thread1", "thread2"],
    }
    mock_response = Mock(spec=httpx.Response, json=lambda: user_data)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.users.get("testuser")

    assert result.username == "testuser"
    assert result.password == "hashedpwd"
    assert result.dateCreated == 1736234567890
    assert result.grantedAuthorities == ["ROLE_USER", "READ_REPO_test"]
    assert result.appSettings == {"theme": "dark", "language": "en"}
    assert result.gptThreads == ["thread1", "thread2"]


def test_get_user_handles_null_optional_fields(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that get handles null values for optional fields."""
    user_data = {
        "username": "testuser",
        "password": "",
        "dateCreated": 1736234567890,
        "grantedAuthorities": None,
        "appSettings": None,
        "gptThreads": None,
    }
    mock_response = Mock(spec=httpx.Response, json=lambda: user_data)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.users.get("testuser")

    # User.__post_init__ normalizes None to empty collections
    assert result.grantedAuthorities == []
    assert result.appSettings == {}
    assert result.gptThreads == []


def test_get_user_raises_response_format_error_on_json_parse_error(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that get raises ResponseFormatError when JSON parsing fails."""
    mock_response = Mock(spec=httpx.Response)
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(ResponseFormatError, match="Failed to parse GraphDB response"):
        client.users.get("admin")


def test_get_user_raises_response_format_error_on_invalid_user_data(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that get raises ResponseFormatError when user data is invalid."""
    # Missing required field 'username'
    user_data = {
        "password": "",
        "dateCreated": 1736234567890,
    }
    mock_response = Mock(spec=httpx.Response, json=lambda: user_data)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(ResponseFormatError, match="Failed to parse GraphDB response"):
        client.users.get("admin")


def test_get_user_raises_forbidden_error(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that get raises ForbiddenError for 403 responses."""
    mock_response = Mock(spec=httpx.Response, status_code=403, text="Forbidden")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "HTTP 403",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(ForbiddenError, match="Request is forbidden"):
        client.users.get("admin")


def test_get_user_raises_not_found_error(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that get raises NotFoundError for 404 responses."""
    mock_response = Mock(spec=httpx.Response, status_code=404, text="Not found")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "HTTP 404",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(NotFoundError, match="User not found"):
        client.users.get("nonexistent")


def test_get_user_raises_internal_server_error(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that get raises InternalServerError for 500 responses."""
    error_text = "Database connection failed"
    mock_response = Mock(spec=httpx.Response, status_code=500, text=error_text)
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "HTTP 500",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(InternalServerError, match=error_text):
        client.users.get("admin")


@pytest.mark.parametrize(
    "status_code",
    [400, 401, 409, 502, 503],
)
def test_get_user_reraises_other_http_errors(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
):
    """Test that get re-raises HTTPStatusError for unhandled status codes."""
    mock_response = Mock(spec=httpx.Response, status_code=status_code, text="Error")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        f"HTTP {status_code}",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(httpx.HTTPStatusError):
        client.users.get("admin")
