from __future__ import annotations

import pytest

from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    from rdflib.contrib.graphdb.models import (
        FreeAccessSettings,
        GraphDBRepository,
        OWLimParameter,
        RepositoryConfigBeanCreate,
        RepositoryState,
        User,
    )


def test_repository_config_bean_create_to_dict_basic():
    """Test basic serialization of RepositoryConfigBeanCreate to dict."""
    config = RepositoryConfigBeanCreate(
        id="test-repo",
        title="Test Repository",
        type="graphdb:FreeSailRepository",
        sesameType="graphdb:FreeSailRepository",
        location="",
    )

    result = config.as_dict()

    assert isinstance(result, dict)
    assert result["id"] == "test-repo"
    assert result["title"] == "Test Repository"
    assert result["type"] == "graphdb:FreeSailRepository"
    assert result["sesameType"] == "graphdb:FreeSailRepository"
    assert result["location"] == ""
    assert result["params"] == {}
    assert result["missingDefaults"] == {}


def test_repository_config_bean_create_to_dict_with_params():
    """Test serialization with params containing OWLimParameter objects."""
    param1 = OWLimParameter(name="param1", label="Parameter 1", value="value1")
    param2 = OWLimParameter(name="param2", label="Parameter 2", value="value2")

    config = RepositoryConfigBeanCreate(
        id="test-repo",
        title="Test Repository",
        type="graphdb:FreeSailRepository",
        sesameType="graphdb:FreeSailRepository",
        location="",
        params={"param1": param1, "param2": param2},
    )

    result = config.as_dict()

    assert isinstance(result, dict)
    assert "params" in result
    assert isinstance(result["params"], dict)
    assert len(result["params"]) == 2

    assert result["params"]["param1"]["name"] == "param1"
    assert result["params"]["param1"]["label"] == "Parameter 1"
    assert result["params"]["param1"]["value"] == "value1"

    assert result["params"]["param2"]["name"] == "param2"
    assert result["params"]["param2"]["label"] == "Parameter 2"
    assert result["params"]["param2"]["value"] == "value2"


def test_repository_config_bean_create_to_dict_with_missing_defaults():
    """Test serialization with missingDefaults containing OWLimParameter objects."""
    default1 = OWLimParameter(
        name="default1", label="Default 1", value="default_value1"
    )

    config = RepositoryConfigBeanCreate(
        id="test-repo",
        title="Test Repository",
        type="graphdb:FreeSailRepository",
        sesameType="graphdb:FreeSailRepository",
        location="",
        missingDefaults={"default1": default1},
    )

    result = config.as_dict()

    assert isinstance(result, dict)
    assert "missingDefaults" in result
    assert isinstance(result["missingDefaults"], dict)
    assert len(result["missingDefaults"]) == 1

    assert result["missingDefaults"]["default1"]["name"] == "default1"
    assert result["missingDefaults"]["default1"]["label"] == "Default 1"
    assert result["missingDefaults"]["default1"]["value"] == "default_value1"


def test_repository_config_bean_create_to_dict_complete():
    """Test serialization with all fields populated."""
    param1 = OWLimParameter(name="param1", label="Parameter 1", value="value1")
    default1 = OWLimParameter(
        name="default1", label="Default 1", value="default_value1"
    )

    config = RepositoryConfigBeanCreate(
        id="test-repo",
        title="Test Repository",
        type="graphdb:FreeSailRepository",
        sesameType="graphdb:FreeSailRepository",
        location="/path/to/repo",
        params={"param1": param1},
        missingDefaults={"default1": default1},
    )

    result = config.as_dict()

    assert isinstance(result, dict)
    assert result["id"] == "test-repo"
    assert result["title"] == "Test Repository"
    assert result["type"] == "graphdb:FreeSailRepository"
    assert result["sesameType"] == "graphdb:FreeSailRepository"
    assert result["location"] == "/path/to/repo"
    assert len(result["params"]) == 1
    assert len(result["missingDefaults"]) == 1


def test_repository_config_bean_create_to_dict_json_serializable():
    """Test that the result is JSON serializable (required for httpx)."""
    import json

    param1 = OWLimParameter(name="param1", label="Parameter 1", value="value1")

    config = RepositoryConfigBeanCreate(
        id="test-repo",
        title="Test Repository",
        type="graphdb:FreeSailRepository",
        sesameType="graphdb:FreeSailRepository",
        location="",
        params={"param1": param1},
    )

    result = config.as_dict()

    # Should be able to serialize to JSON without errors
    json_str = json.dumps(result)
    assert isinstance(json_str, str)

    # Should be able to deserialize back
    deserialized = json.loads(json_str)
    assert deserialized == result


def test_graphdb_repository_from_dict_basic():
    """GraphDBRepository.from_dict should map basic fields."""
    data = {
        "id": "repo1",
        "title": "Repo 1",
        "type": "graphdb:FreeSailRepository",
        "sesameType": "graphdb:FreeSailRepository",
        "location": "/data",
        "local": True,
        "readable": True,
        "writable": False,
        "unsupported": False,
    }

    repo = GraphDBRepository.from_dict(data)

    assert repo.id == "repo1"
    assert repo.title == "Repo 1"
    assert repo.type == "graphdb:FreeSailRepository"
    assert repo.sesameType == "graphdb:FreeSailRepository"
    assert repo.location == "/data"
    assert repo.local is True
    assert repo.readable is True
    assert repo.writable is False
    assert repo.unsupported is False
    assert repo.state is None


def test_graphdb_repository_from_dict_state_enum():
    """State strings should be converted to RepositoryState enums."""
    data = {
        "id": "repo2",
        "state": "RUNNING",
    }

    repo = GraphDBRepository.from_dict(data)

    assert repo.id == "repo2"
    assert repo.state == RepositoryState.RUNNING


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
        dateCreated="2024-01-01T00:00:00Z",
        grantedAuthorities=["ROLE_USER", "ROLE_ADMIN"],
        appSettings={"theme": "dark", "maxAge": 3600},
        gptThreads=[{"id": 1, "name": "thread1"}],
    )

    assert user.username == "testuser"
    assert user.password == "password123"
    assert user.dateCreated == "2024-01-01T00:00:00Z"
    assert user.grantedAuthorities == ["ROLE_USER", "ROLE_ADMIN"]
    assert user.appSettings == {"theme": "dark", "maxAge": 3600}
    assert user.gptThreads == [{"id": 1, "name": "thread1"}]


def test_user_minimal():
    """Test creating a User with only required fields."""
    user = User(
        username="testuser",
        password="password123",
        dateCreated="2024-01-01T00:00:00Z",
    )

    assert user.username == "testuser"
    assert user.password == "password123"
    assert user.dateCreated == "2024-01-01T00:00:00Z"
    assert user.grantedAuthorities == []
    assert user.appSettings == {}
    assert user.gptThreads == []


def test_user_normalize_none_app_settings():
    """Test that None appSettings is normalized to empty dict."""
    user = User(
        username="testuser",
        password="password123",
        dateCreated="2024-01-01T00:00:00Z",
        appSettings=None,
    )

    assert user.appSettings == {}


def test_user_normalize_none_gpt_threads():
    """Test that None gptThreads is normalized to empty list."""
    user = User(
        username="testuser",
        password="password123",
        dateCreated="2024-01-01T00:00:00Z",
        gptThreads=None,
    )

    assert user.gptThreads == []


def test_user_normalize_none_granted_authorities():
    """Test that None grantedAuthorities is normalized to empty list."""
    user = User(
        username="testuser",
        password="password123",
        dateCreated="2024-01-01T00:00:00Z",
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
            dateCreated="2024-01-01T00:00:00Z",
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
            dateCreated="2024-01-01T00:00:00Z",
        )


@pytest.mark.parametrize(
    "date_created",
    [123, None, [], {}],
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
            dateCreated="2024-01-01T00:00:00Z",
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
            dateCreated="2024-01-01T00:00:00Z",
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
            dateCreated="2024-01-01T00:00:00Z",
            appSettings=app_settings,
        )


def test_user_invalid_app_settings_key():
    """Test that non-string keys in appSettings raise ValueError."""
    with pytest.raises(ValueError):
        User(
            username="testuser",
            password="password123",
            dateCreated="2024-01-01T00:00:00Z",
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
            dateCreated="2024-01-01T00:00:00Z",
            gptThreads=gpt_threads,
        )


def test_user_as_dict():
    """Test User.as_dict() serialization."""
    user = User(
        username="testuser",
        password="password123",
        dateCreated="2024-01-01T00:00:00Z",
        grantedAuthorities=["ROLE_USER"],
        appSettings={"theme": "dark"},
        gptThreads=[{"id": 1}],
    )

    result = user.as_dict()

    assert isinstance(result, dict)
    assert result["username"] == "testuser"
    assert result["password"] == "password123"
    assert result["dateCreated"] == "2024-01-01T00:00:00Z"
    assert result["grantedAuthorities"] == ["ROLE_USER"]
    assert result["appSettings"] == {"theme": "dark"}
    assert result["gptThreads"] == [{"id": 1}]
