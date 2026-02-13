from __future__ import annotations

import pytest

from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    from rdflib import URIRef
    from rdflib.contrib.graphdb.models import (
        AccessControlEntry,
        ClearGraphAccessControlEntry,
        FreeAccessSettings,
        PluginAccessControlEntry,
        StatementAccessControlEntry,
        SystemAccessControlEntry,
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


def test_access_control_entry_from_dict_system_scope():
    """Test creating SystemAccessControlEntry from dict with 'system' scope."""
    data = {
        "scope": "system",
        "policy": "allow",
        "role": "admin",
        "operation": "read",
    }

    result = AccessControlEntry.from_dict(data)

    assert isinstance(result, SystemAccessControlEntry)
    assert result.scope == "system"
    assert result.policy == "allow"
    assert result.role == "admin"
    assert result.operation == "read"


def test_access_control_entry_from_dict_statement_scope():
    """Test creating StatementAccessControlEntry from dict with 'statement' scope."""
    data = {
        "scope": "statement",
        "policy": "deny",
        "role": "user",
        "operation": "write",
        "subject": "<http://example.org/subject>",
        "predicate": "<http://example.org/predicate>",
        "object": "<http://example.org/object>",
        "context": "<http://example.org/graph>",
    }

    result = AccessControlEntry.from_dict(data)

    assert isinstance(result, StatementAccessControlEntry)
    assert result.scope == "statement"
    assert result.policy == "deny"
    assert result.role == "user"
    assert result.operation == "write"
    assert result.subject == URIRef("http://example.org/subject")
    assert result.predicate == URIRef("http://example.org/predicate")
    assert result.object == URIRef("http://example.org/object")
    assert result.graph == URIRef("http://example.org/graph")


def test_access_control_entry_from_dict_plugin_scope():
    """Test creating PluginAccessControlEntry from dict with 'plugin' scope."""
    data = {
        "scope": "plugin",
        "policy": "abstain",
        "role": "editor",
        "operation": "*",
        "plugin": "elasticsearch-connector",
    }

    result = AccessControlEntry.from_dict(data)

    assert isinstance(result, PluginAccessControlEntry)
    assert result.scope == "plugin"
    assert result.policy == "abstain"
    assert result.role == "editor"
    assert result.operation == "*"
    assert result.plugin == "elasticsearch-connector"


def test_access_control_entry_from_dict_clear_graph_scope():
    """Test creating ClearGraphAccessControlEntry from dict with 'clear_graph' scope."""
    data = {
        "scope": "clear_graph",
        "policy": "allow",
        "role": "admin",
        "context": "named",
    }

    result = AccessControlEntry.from_dict(data)

    assert isinstance(result, ClearGraphAccessControlEntry)
    assert result.scope == "clear_graph"
    assert result.policy == "allow"
    assert result.role == "admin"
    assert result.graph == "named"


def test_access_control_entry_from_dict_not_dict():
    """Test that from_dict raises TypeError when input is not a dict."""
    with pytest.raises(TypeError, match="ACL entry must be a mapping"):
        AccessControlEntry.from_dict("not a dict")


def test_access_control_entry_from_dict_list_input():
    """Test that from_dict raises TypeError when input is a list."""
    with pytest.raises(TypeError, match="ACL entry must be a mapping"):
        AccessControlEntry.from_dict([{"scope": "system"}])


@pytest.mark.parametrize(
    "scope",
    ["unknown", "invalid", "", None, 123, "Statement"],
)
def test_access_control_entry_from_dict_invalid_scope(scope):
    """Test that from_dict raises ValueError for invalid or unsupported scope values."""
    data = {
        "scope": scope,
        "policy": "allow",
        "role": "admin",
    }

    with pytest.raises(ValueError):
        AccessControlEntry.from_dict(data)


@pytest.mark.parametrize(
    "policy",
    ["invalid", "ALLOW", "", None, 123],
)
def test_access_control_entry_from_dict_invalid_policy(policy):
    """Test that from_dict raises ValueError for invalid policy values."""
    data = {
        "scope": "system",
        "policy": policy,
        "role": "admin",
        "operation": "read",
    }

    with pytest.raises(ValueError):
        AccessControlEntry.from_dict(data)


@pytest.mark.parametrize(
    "operation",
    ["invalid", "READ", "", None, 123],
)
def test_access_control_entry_from_dict_invalid_operation(operation):
    """Test that from_dict raises ValueError for invalid operation values."""
    data = {
        "scope": "system",
        "policy": "allow",
        "role": "admin",
        "operation": operation,
    }

    with pytest.raises(ValueError):
        AccessControlEntry.from_dict(data)


@pytest.mark.parametrize(
    "role",
    [123, None, [], {}],
)
def test_access_control_entry_from_dict_invalid_role(role):
    """Test that from_dict raises ValueError for invalid role values."""
    data = {
        "scope": "system",
        "policy": "allow",
        "role": role,
        "operation": "read",
    }

    with pytest.raises(ValueError):
        AccessControlEntry.from_dict(data)


def test_access_control_entry_from_dict_invalid_plugin():
    """Test that from_dict raises ValueError for invalid plugin values."""
    data = {
        "scope": "plugin",
        "policy": "allow",
        "role": "admin",
        "operation": "read",
        "plugin": 123,  # Should be string
    }

    with pytest.raises(ValueError):
        AccessControlEntry.from_dict(data)


def test_access_control_entry_from_dict_invalid_subject():
    """Test that from_dict raises ValueError for invalid subject values."""
    data = {
        "scope": "statement",
        "policy": "allow",
        "role": "admin",
        "operation": "read",
        "subject": 123,  # Should be string or "*" or URIRef
        "predicate": "*",
        "object": "*",
        "context": "*",
    }

    with pytest.raises(ValueError):
        AccessControlEntry.from_dict(data)
