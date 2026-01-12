from __future__ import annotations

import pytest

from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    from rdflib.contrib.graphdb.models import (
        FreeAccessSettings,
        User,
    )


def test_free_access_settings_valid():
    settings = FreeAccessSettings(
        enabled=True,
        authorities=["ROLE_USER"],
        appSettings={"maxAge": 3600},
    )

    assert settings.enabled is True
    assert settings.authorities == ["ROLE_USER"]
    assert settings.appSettings == {"maxAge": 3600}


@pytest.mark.parametrize(
    "enabled",
    [1, "true", None],
)
def test_free_access_settings_invalid_enabled(enabled):
    with pytest.raises(ValueError):
        FreeAccessSettings(enabled=enabled)


@pytest.mark.parametrize(
    "authorities",
    ["ROLE_USER", ["ROLE_USER", 1], [1], {"ROLE_USER": True}],
)
def test_free_access_settings_invalid_authorities(authorities):
    with pytest.raises(ValueError):
        FreeAccessSettings(enabled=True, authorities=authorities)


@pytest.mark.parametrize(
    "app_settings",
    ["value", ["setting"], 1],
)
def test_free_access_settings_invalid_app_settings_type(app_settings):
    with pytest.raises(ValueError):
        FreeAccessSettings(enabled=True, appSettings=app_settings)


def test_free_access_settings_invalid_app_settings_key():
    with pytest.raises(ValueError):
        FreeAccessSettings(enabled=True, appSettings={1: "value"})


def test_user_valid():
    """Test creating a valid User."""
    user = User(
        username="testuser",
        password="password123",
        dateCreated=1704067200,
        grantedAuthorities=["ROLE_USER", "ROLE_ADMIN"],
        appSettings={"theme": "dark", "maxAge": 3600},
        gptThreads=[{"id": 1, "name": "thread1"}],
    )

    assert user.username == "testuser"
    assert user.password == "password123"
    assert user.dateCreated == 1704067200
    assert user.grantedAuthorities == ["ROLE_USER", "ROLE_ADMIN"]
    assert user.appSettings == {"theme": "dark", "maxAge": 3600}
    assert user.gptThreads == [{"id": 1, "name": "thread1"}]


def test_user_minimal():
    """Test creating a User with only required fields."""
    user = User(
        username="testuser",
        password="password123",
        dateCreated=1704067200,
    )

    assert user.username == "testuser"
    assert user.password == "password123"
    assert user.dateCreated == 1704067200
    assert user.grantedAuthorities == []
    assert user.appSettings == {}
    assert user.gptThreads == []


def test_user_normalize_none_app_settings():
    """Test that None appSettings is normalized to empty dict."""
    user = User(
        username="testuser",
        password="password123",
        dateCreated=1704067200,
        appSettings=None,
    )

    assert user.appSettings == {}


def test_user_normalize_none_gpt_threads():
    """Test that None gptThreads is normalized to empty list."""
    user = User(
        username="testuser",
        password="password123",
        dateCreated=1704067200,
        gptThreads=None,
    )

    assert user.gptThreads == []


def test_user_normalize_none_granted_authorities():
    """Test that None grantedAuthorities is normalized to empty list."""
    user = User(
        username="testuser",
        password="password123",
        dateCreated=1704067200,
        grantedAuthorities=None,
    )

    assert user.grantedAuthorities == []


@pytest.mark.parametrize(
    "username",
    [123, None, [], {}],
)
def test_user_invalid_username(username):
    """Test that invalid username types raise ValueError."""
    with pytest.raises(ValueError):
        User(
            username=username,
            password="password123",
            dateCreated=1704067200,
        )


@pytest.mark.parametrize(
    "password",
    [123, None, [], {}],
)
def test_user_invalid_password(password):
    """Test that invalid password types raise ValueError."""
    with pytest.raises(ValueError):
        User(
            username="testuser",
            password=password,
            dateCreated=1704067200,
        )


@pytest.mark.parametrize(
    "date_created",
    ["2024-01-01T00:00:00Z", None, [], {}, 1.5],
)
def test_user_invalid_date_created(date_created):
    """Test that invalid dateCreated types raise ValueError."""
    with pytest.raises(ValueError):
        User(
            username="testuser",
            password="password123",
            dateCreated=date_created,
        )


@pytest.mark.parametrize(
    "granted_authorities",
    ["ROLE_USER", {"ROLE_USER": True}, 123],
)
def test_user_invalid_granted_authorities_type(granted_authorities):
    """Test that invalid grantedAuthorities types raise ValueError."""
    with pytest.raises(ValueError):
        User(
            username="testuser",
            password="password123",
            dateCreated=1704067200,
            grantedAuthorities=granted_authorities,
        )


@pytest.mark.parametrize(
    "granted_authorities",
    [["ROLE_USER", 123], [1, 2, 3], ["ROLE_USER", None]],
)
def test_user_invalid_granted_authorities_elements(granted_authorities):
    """Test that non-string elements in grantedAuthorities raise ValueError."""
    with pytest.raises(ValueError):
        User(
            username="testuser",
            password="password123",
            dateCreated=1704067200,
            grantedAuthorities=granted_authorities,
        )


@pytest.mark.parametrize(
    "app_settings",
    ["settings", ["setting"], 123],
)
def test_user_invalid_app_settings_type(app_settings):
    """Test that invalid appSettings types raise ValueError."""
    with pytest.raises(ValueError):
        User(
            username="testuser",
            password="password123",
            dateCreated=1704067200,
            appSettings=app_settings,
        )


def test_user_invalid_app_settings_key():
    """Test that non-string keys in appSettings raise ValueError."""
    with pytest.raises(ValueError):
        User(
            username="testuser",
            password="password123",
            dateCreated=1704067200,
            appSettings={1: "value"},
        )


@pytest.mark.parametrize(
    "gpt_threads",
    ["thread", {"thread": 1}, 123],
)
def test_user_invalid_gpt_threads_type(gpt_threads):
    """Test that invalid gptThreads types raise ValueError."""
    with pytest.raises(ValueError):
        User(
            username="testuser",
            password="password123",
            dateCreated=1704067200,
            gptThreads=gpt_threads,
        )


def test_user_as_dict():
    """Test User.as_dict() serialization."""
    user = User(
        username="testuser",
        password="password123",
        dateCreated=1704067200,
        grantedAuthorities=["ROLE_USER"],
        appSettings={"theme": "dark"},
        gptThreads=[{"id": 1}],
    )

    result = user.as_dict()

    assert isinstance(result, dict)
    assert result["username"] == "testuser"
    assert result["password"] == "password123"
    assert result["dateCreated"] == 1704067200
    assert result["grantedAuthorities"] == ["ROLE_USER"]
    assert result["appSettings"] == {"theme": "dark"}
    assert result["gptThreads"] == [{"id": 1}]
