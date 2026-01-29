from __future__ import annotations

import pytest

from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    from rdflib.contrib.graphdb.models import AuthenticatedUser


def test_authenticated_user_valid():
    """Test creating a valid AuthenticatedUser."""
    user = AuthenticatedUser(
        username="admin",
        authorities=["ROLE_USER", "ROLE_ADMIN"],
        appSettings={"DEFAULT_INFERENCE": True},
        external=False,
        token="GDB abc123.signature",
    )

    assert user.username == "admin"
    assert user.authorities == ["ROLE_USER", "ROLE_ADMIN"]
    assert user.appSettings == {"DEFAULT_INFERENCE": True}
    assert user.external is False
    assert user.token == "GDB abc123.signature"


def test_authenticated_user_minimal():
    """Test creating an AuthenticatedUser with only required fields."""
    user = AuthenticatedUser(username="testuser")

    assert user.username == "testuser"
    assert user.authorities == []
    assert user.appSettings == {}
    assert user.external is False
    assert user.token == ""


def test_authenticated_user_normalize_none_authorities():
    """Test that None authorities is normalized to empty list."""
    user = AuthenticatedUser(username="testuser", authorities=None)

    assert user.authorities == []


def test_authenticated_user_normalize_none_app_settings():
    """Test that None appSettings is normalized to empty dict."""
    user = AuthenticatedUser(username="testuser", appSettings=None)

    assert user.appSettings == {}


@pytest.mark.parametrize(
    "username",
    [123, None, [], {}],
)
def test_authenticated_user_invalid_username(username):
    """Test that invalid username types raise ValueError."""
    with pytest.raises(ValueError):
        AuthenticatedUser(username=username)


@pytest.mark.parametrize(
    "authorities",
    ["ROLE_USER", {"ROLE_USER": True}, 123],
)
def test_authenticated_user_invalid_authorities_type(authorities):
    """Test that invalid authorities types raise ValueError."""
    with pytest.raises(ValueError):
        AuthenticatedUser(username="testuser", authorities=authorities)


@pytest.mark.parametrize(
    "authorities",
    [["ROLE_USER", 123], [1, 2, 3], ["ROLE_USER", None]],
)
def test_authenticated_user_invalid_authorities_elements(authorities):
    """Test that non-string elements in authorities raise ValueError."""
    with pytest.raises(ValueError):
        AuthenticatedUser(username="testuser", authorities=authorities)


@pytest.mark.parametrize(
    "app_settings",
    ["settings", ["setting"], 123],
)
def test_authenticated_user_invalid_app_settings_type(app_settings):
    """Test that invalid appSettings types raise ValueError."""
    with pytest.raises(ValueError):
        AuthenticatedUser(username="testuser", appSettings=app_settings)


def test_authenticated_user_invalid_app_settings_key():
    """Test that non-string keys in appSettings raise ValueError."""
    with pytest.raises(ValueError):
        AuthenticatedUser(username="testuser", appSettings={1: "value"})


@pytest.mark.parametrize(
    "external",
    ["true", "false", 1, 0, None],
)
def test_authenticated_user_invalid_external(external):
    """Test that invalid external types raise ValueError."""
    with pytest.raises(ValueError):
        AuthenticatedUser(username="testuser", external=external)


@pytest.mark.parametrize(
    "token",
    [123, None, [], {}],
)
def test_authenticated_user_invalid_token(token):
    """Test that invalid token types raise ValueError."""
    with pytest.raises(ValueError):
        AuthenticatedUser(username="testuser", token=token)


def test_authenticated_user_from_response_valid():
    """Test creating AuthenticatedUser from valid response data."""
    data = {
        "username": "admin",
        "password": "[CREDENTIALS]",
        "authorities": ["ROLE_USER", "ROLE_ADMIN"],
        "appSettings": {"DEFAULT_INFERENCE": True},
        "external": False,
    }
    token = "GDB eyJ1c2VybmFtZSI6ImFkbWluIg==.signature"

    user = AuthenticatedUser.from_response(data, token)

    assert user.username == "admin"
    assert user.authorities == ["ROLE_USER", "ROLE_ADMIN"]
    assert user.appSettings == {"DEFAULT_INFERENCE": True}
    assert user.external is False
    assert user.token == token


def test_authenticated_user_from_response_minimal():
    """Test creating AuthenticatedUser from minimal response data."""
    data = {"username": "testuser"}
    token = "GDB abc123"

    user = AuthenticatedUser.from_response(data, token)

    assert user.username == "testuser"
    assert user.authorities == []
    assert user.appSettings == {}
    assert user.external is False
    assert user.token == token


def test_authenticated_user_from_response_not_dict():
    """Test that from_response raises TypeError when data is not a dict."""
    with pytest.raises(TypeError, match="Response data must be a dict"):
        AuthenticatedUser.from_response("not a dict", "token")


def test_authenticated_user_from_response_list_input():
    """Test that from_response raises TypeError when data is a list."""
    with pytest.raises(TypeError, match="Response data must be a dict"):
        AuthenticatedUser.from_response([{"username": "admin"}], "token")


def test_authenticated_user_from_response_missing_username():
    """Test that from_response raises ValueError when username is missing."""
    data = {"authorities": ["ROLE_USER"]}

    with pytest.raises(ValueError, match="must contain 'username'"):
        AuthenticatedUser.from_response(data, "token")
