from __future__ import annotations

from unittest.mock import Mock

import pytest

from rdflib.contrib.graphdb.exceptions import (
    BadRequestError,
    ForbiddenError,
    GraphDBError,
    InternalServerError,
    NotFoundError,
    PreconditionFailedError,
    ResponseFormatError,
    UnauthorisedError,
)
from rdflib.contrib.graphdb.models import User, UserCreate, UserUpdate
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


def test_overwrite_user_success(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that overwrite sends a PUT request with correct headers and body."""
    user = User(
        username="admin",
        password="newpass",
        dateCreated=1736234567890,
        grantedAuthorities=["ROLE_ADMIN"],
        appSettings={},
        gptThreads=[],
    )
    mock_response = Mock(spec=httpx.Response)
    mock_httpx_put = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "put", mock_httpx_put)

    result = client.users.overwrite("admin", user)

    assert result is None
    mock_httpx_put.assert_called_once_with(
        "/rest/security/users/admin",
        headers={"Content-Type": "application/json"},
        json=user.as_dict(),
    )
    mock_response.raise_for_status.assert_called_once()


def test_overwrite_user_raises_type_error_for_non_string_username(
    client: GraphDBClient,
):
    """Test that overwrite raises TypeError when username is not a string."""
    user = User(
        username="admin",
        password="",
        dateCreated=1736234567890,
        grantedAuthorities=["ROLE_ADMIN"],
    )

    with pytest.raises(TypeError, match="Username must be a string"):
        client.users.overwrite(123, user)


def test_overwrite_user_raises_type_error_for_non_user_object(
    client: GraphDBClient,
):
    """Test that overwrite raises TypeError when user is not a User instance."""
    with pytest.raises(TypeError, match="User must be an instance of User"):
        client.users.overwrite("admin", {"username": "admin"})


def test_overwrite_user_raises_unauthorised_error(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that overwrite raises UnauthorisedError for 401 responses."""
    user = User(
        username="admin",
        password="",
        dateCreated=1736234567890,
        grantedAuthorities=["ROLE_ADMIN"],
    )
    mock_response = Mock(spec=httpx.Response, status_code=401, text="Unauthorized")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "HTTP 401",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_put = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "put", mock_httpx_put)

    with pytest.raises(UnauthorisedError, match="Request is unauthorised"):
        client.users.overwrite("admin", user)


def test_overwrite_user_raises_forbidden_error(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that overwrite raises ForbiddenError for 403 responses."""
    user = User(
        username="admin",
        password="",
        dateCreated=1736234567890,
        grantedAuthorities=["ROLE_ADMIN"],
    )
    mock_response = Mock(spec=httpx.Response, status_code=403, text="Forbidden")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "HTTP 403",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_put = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "put", mock_httpx_put)

    with pytest.raises(ForbiddenError, match="Request is forbidden"):
        client.users.overwrite("admin", user)


def test_overwrite_user_raises_not_found_error(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that overwrite raises NotFoundError for 404 responses."""
    user = User(
        username="nonexistent",
        password="",
        dateCreated=1736234567890,
        grantedAuthorities=["ROLE_USER"],
    )
    mock_response = Mock(spec=httpx.Response, status_code=404, text="Not found")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "HTTP 404",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_put = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "put", mock_httpx_put)

    with pytest.raises(NotFoundError, match="User not found"):
        client.users.overwrite("nonexistent", user)


@pytest.mark.parametrize(
    "status_code",
    [400, 409, 500, 502, 503],
)
def test_overwrite_user_reraises_other_http_errors(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
):
    """Test that overwrite re-raises HTTPStatusError for unhandled status codes."""
    user = User(
        username="admin",
        password="",
        dateCreated=1736234567890,
        grantedAuthorities=["ROLE_ADMIN"],
    )
    mock_response = Mock(spec=httpx.Response, status_code=status_code, text="Error")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        f"HTTP {status_code}",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_put = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "put", mock_httpx_put)

    with pytest.raises(httpx.HTTPStatusError):
        client.users.overwrite("admin", user)


def test_create_user_success(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that create sends a POST request with correct headers and body."""
    user = UserCreate(
        username="newuser",
        password="password123",
        grantedAuthorities=["ROLE_USER"],
        appSettings={},
        gptThreads=[],
    )
    mock_response = Mock(spec=httpx.Response)
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    result = client.users.create("newuser", user)

    assert result is None
    mock_httpx_post.assert_called_once_with(
        "/rest/security/users/newuser",
        headers={"Content-Type": "application/json"},
        json=user.as_dict(),
    )
    mock_response.raise_for_status.assert_called_once()


def test_create_user_raises_type_error_for_non_string_username(
    client: GraphDBClient,
):
    """Test that create raises TypeError when username is not a string."""
    user = UserCreate(
        username="newuser",
        password="password123",
        grantedAuthorities=["ROLE_USER"],
    )

    with pytest.raises(TypeError, match="Username must be a string"):
        client.users.create(123, user)


def test_create_user_raises_type_error_for_non_user_object(
    client: GraphDBClient,
):
    """Test that create raises TypeError when user is not a UserCreate instance."""
    with pytest.raises(TypeError, match="User must be an instance of UserCreate"):
        client.users.create("newuser", {"username": "newuser"})


def test_create_user_raises_bad_request_error(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that create raises BadRequestError for 400 responses."""
    user = UserCreate(
        username="newuser",
        password="password123",
        grantedAuthorities=["ROLE_USER"],
    )
    error_text = "Invalid user data"
    mock_response = Mock(spec=httpx.Response, status_code=400, text=error_text)
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "HTTP 400",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    with pytest.raises(BadRequestError, match="Bad request"):
        client.users.create("newuser", user)


def test_create_user_bad_request_error_includes_response_text(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that BadRequestError includes the response text in the message."""
    user = UserCreate(
        username="newuser",
        password="password123",
        grantedAuthorities=["ROLE_USER"],
    )
    error_text = "User already exists"
    mock_response = Mock(spec=httpx.Response, status_code=400, text=error_text)
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "HTTP 400",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    with pytest.raises(BadRequestError, match=error_text):
        client.users.create("newuser", user)


def test_create_user_raises_unauthorised_error(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that create raises UnauthorisedError for 401 responses."""
    user = UserCreate(
        username="newuser",
        password="password123",
        grantedAuthorities=["ROLE_USER"],
    )
    mock_response = Mock(spec=httpx.Response, status_code=401, text="Unauthorized")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "HTTP 401",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    with pytest.raises(UnauthorisedError, match="Request is unauthorised"):
        client.users.create("newuser", user)


def test_create_user_raises_forbidden_error(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that create raises ForbiddenError for 403 responses."""
    user = UserCreate(
        username="newuser",
        password="password123",
        grantedAuthorities=["ROLE_USER"],
    )
    mock_response = Mock(spec=httpx.Response, status_code=403, text="Forbidden")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "HTTP 403",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    with pytest.raises(ForbiddenError, match="Request is forbidden"):
        client.users.create("newuser", user)


@pytest.mark.parametrize(
    "status_code",
    [404, 409, 500, 502, 503],
)
def test_create_user_reraises_other_http_errors(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
):
    """Test that create re-raises HTTPStatusError for unhandled status codes."""
    user = UserCreate(
        username="newuser",
        password="password123",
        grantedAuthorities=["ROLE_USER"],
    )
    mock_response = Mock(spec=httpx.Response, status_code=status_code, text="Error")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        f"HTTP {status_code}",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_post = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    with pytest.raises(httpx.HTTPStatusError):
        client.users.create("newuser", user)


def test_delete_user_success(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that delete sends a DELETE request with the correct endpoint."""
    mock_response = Mock(spec=httpx.Response)
    mock_httpx_delete = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "delete", mock_httpx_delete)

    result = client.users.delete("testuser")

    assert result is None
    mock_httpx_delete.assert_called_once_with("/rest/security/users/testuser")
    mock_response.raise_for_status.assert_called_once()


def test_delete_user_raises_type_error_for_non_string_username(
    client: GraphDBClient,
):
    """Test that delete raises TypeError when username is not a string."""
    with pytest.raises(TypeError, match="Username must be a string"):
        client.users.delete(123)


def test_delete_user_raises_bad_request_error(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that delete raises BadRequestError for 400 responses."""
    error_text = "Bad request"
    mock_response = Mock(spec=httpx.Response, status_code=400, text=error_text)
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "HTTP 400",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_delete = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "delete", mock_httpx_delete)

    with pytest.raises(BadRequestError, match="Bad request"):
        client.users.delete("testuser")


def test_delete_user_bad_request_error_includes_response_text(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that BadRequestError includes the response text in the message."""
    error_text = "Cannot delete last admin user"
    mock_response = Mock(spec=httpx.Response, status_code=400, text=error_text)
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "HTTP 400",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_delete = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "delete", mock_httpx_delete)

    with pytest.raises(BadRequestError, match=error_text):
        client.users.delete("admin")


def test_delete_user_raises_unauthorised_error(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that delete raises UnauthorisedError for 401 responses."""
    mock_response = Mock(spec=httpx.Response, status_code=401, text="Unauthorized")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "HTTP 401",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_delete = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "delete", mock_httpx_delete)

    with pytest.raises(UnauthorisedError, match="Request is unauthorised"):
        client.users.delete("testuser")


def test_delete_user_raises_forbidden_error(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that delete raises ForbiddenError for 403 responses."""
    mock_response = Mock(spec=httpx.Response, status_code=403, text="Forbidden")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "HTTP 403",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_delete = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "delete", mock_httpx_delete)

    with pytest.raises(ForbiddenError, match="Request is forbidden"):
        client.users.delete("testuser")


def test_delete_user_raises_not_found_error(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that delete raises NotFoundError for 404 responses."""
    mock_response = Mock(spec=httpx.Response, status_code=404, text="Not found")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "HTTP 404",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_delete = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "delete", mock_httpx_delete)

    with pytest.raises(NotFoundError, match="User not found"):
        client.users.delete("nonexistent")


@pytest.mark.parametrize(
    "status_code",
    [409, 500, 502, 503],
)
def test_delete_user_reraises_other_http_errors(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
):
    """Test that delete re-raises HTTPStatusError for unhandled status codes."""
    mock_response = Mock(spec=httpx.Response, status_code=status_code, text="Error")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        f"HTTP {status_code}",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_delete = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "delete", mock_httpx_delete)

    with pytest.raises(httpx.HTTPStatusError):
        client.users.delete("testuser")


def test_update_user_success(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that update sends a PATCH request with correct headers and body."""
    user_dict = {"appSettings": {"theme": "dark"}}
    mock_response = Mock(spec=httpx.Response)
    mock_httpx_patch = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "patch", mock_httpx_patch)

    result = client.users.update("admin", user_dict)

    assert result is None
    mock_httpx_patch.assert_called_once_with(
        "/rest/security/users/admin",
        headers={"Content-Type": "application/json"},
        json=user_dict,
    )
    mock_response.raise_for_status.assert_called_once()


def test_update_user_success_with_user_update_model(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that update works with UserUpdate model and serializes it correctly."""
    user_update = UserUpdate(
        password="",
        appSettings={"theme": "dark"},
        gptThreads=[],
    )
    mock_response = Mock(spec=httpx.Response)
    mock_httpx_patch = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "patch", mock_httpx_patch)

    result = client.users.update("admin", user_update)

    assert result is None
    mock_httpx_patch.assert_called_once_with(
        "/rest/security/users/admin",
        headers={"Content-Type": "application/json"},
        json=user_update.as_dict(),
    )
    mock_response.raise_for_status.assert_called_once()


def test_update_user_raises_type_error_for_non_string_username(
    client: GraphDBClient,
):
    """Test that update raises TypeError when username is not a string."""
    user_dict = {"appSettings": {"theme": "dark"}}

    with pytest.raises(TypeError, match="Username must be a string"):
        client.users.update(123, user_dict)


def test_update_user_raises_type_error_for_invalid_user(
    client: GraphDBClient,
):
    """Test that update raises TypeError when user is not a UserUpdate or dict."""
    with pytest.raises(
        TypeError, match="User must be an instance of UserUpdate or dict"
    ):
        client.users.update("admin", "invalid")


def test_update_user_raises_forbidden_error(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that update raises ForbiddenError for 403 responses."""
    user_dict = {"appSettings": {"theme": "dark"}}
    mock_response = Mock(spec=httpx.Response, status_code=403, text="Forbidden")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "HTTP 403",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_patch = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "patch", mock_httpx_patch)

    with pytest.raises(ForbiddenError, match="Request is forbidden"):
        client.users.update("admin", user_dict)


def test_update_user_raises_precondition_failed_error(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that update raises PreconditionFailedError for 412 responses."""
    user_dict = {"appSettings": {"theme": "dark"}}
    mock_response = Mock(
        spec=httpx.Response, status_code=412, text="Precondition failed"
    )
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "HTTP 412",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_patch = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "patch", mock_httpx_patch)

    with pytest.raises(PreconditionFailedError, match="Precondition failed"):
        client.users.update("admin", user_dict)


@pytest.mark.parametrize(
    "status_code",
    [400, 401, 404, 409, 500, 502, 503],
)
def test_update_user_reraises_other_http_errors(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
):
    """Test that update re-raises HTTPStatusError for unhandled status codes."""
    user_dict = {"appSettings": {"theme": "dark"}}
    mock_response = Mock(spec=httpx.Response, status_code=status_code, text="Error")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        f"HTTP {status_code}",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_patch = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "patch", mock_httpx_patch)

    with pytest.raises(httpx.HTTPStatusError):
        client.users.update("admin", user_dict)


def test_custom_roles_returns_list(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that custom_roles returns a list of custom roles."""
    roles_data = ["custom_role_1", "custom_role_2"]
    mock_response = Mock(spec=httpx.Response, json=lambda: roles_data)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.users.custom_roles("admin")

    assert result == ["custom_role_1", "custom_role_2"]
    mock_httpx_get.assert_called_once_with("/rest/security/users/admin/custom-roles")
    mock_response.raise_for_status.assert_called_once()


def test_custom_roles_returns_empty_list(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that custom_roles returns an empty list when no custom roles exist."""
    mock_response = Mock(spec=httpx.Response, json=lambda: [])
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    result = client.users.custom_roles("testuser")

    assert result == []


def test_custom_roles_raises_type_error_for_non_string_username(
    client: GraphDBClient,
):
    """Test that custom_roles raises TypeError when username is not a string."""
    with pytest.raises(TypeError, match="Username must be a string"):
        client.users.custom_roles(123)


def test_custom_roles_raises_forbidden_error(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that custom_roles raises ForbiddenError for 403 responses."""
    mock_response = Mock(spec=httpx.Response, status_code=403, text="Forbidden")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "HTTP 403",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(ForbiddenError, match="Request is forbidden"):
        client.users.custom_roles("admin")


def test_custom_roles_raises_not_found_error(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that custom_roles raises NotFoundError for 404 responses."""
    mock_response = Mock(spec=httpx.Response, status_code=404, text="Not found")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "HTTP 404",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(NotFoundError, match="User not found"):
        client.users.custom_roles("nonexistent")


def test_custom_roles_raises_internal_server_error(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that custom_roles raises InternalServerError for 500 responses."""
    error_text = "Internal server error"
    mock_response = Mock(spec=httpx.Response, status_code=500, text=error_text)
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "HTTP 500",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(InternalServerError, match="Internal server error"):
        client.users.custom_roles("admin")


@pytest.mark.parametrize(
    "status_code",
    [400, 401, 409, 502, 503],
)
def test_custom_roles_reraises_other_http_errors(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
):
    """Test that custom_roles re-raises HTTPStatusError for unhandled status codes."""
    mock_response = Mock(spec=httpx.Response, status_code=status_code, text="Error")
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        f"HTTP {status_code}",
        request=Mock(),
        response=mock_response,
    )
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    with pytest.raises(httpx.HTTPStatusError):
        client.users.custom_roles("admin")
