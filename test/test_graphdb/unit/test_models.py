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
        ImportSettings,
        OWLimParameter,
        ParserSettings,
        RepositoryConfigBeanCreate,
        RepositoryState,
        ServerImportBody,
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


# ==================== ParserSettings Tests ====================


def test_parser_settings_defaults():
    """Test ParserSettings with all default values."""
    settings = ParserSettings()

    assert settings.preserveBNodeIds is False
    assert settings.failOnUnknownDataTypes is False
    assert settings.verifyDataTypeValues is False
    assert settings.normalizeDataTypeValues is False
    assert settings.failOnUnknownLanguageTags is False
    assert settings.verifyLanguageTags is True
    assert settings.normalizeLanguageTags is False
    assert settings.stopOnError is True
    assert settings.contextLink is None


def test_parser_settings_custom_values():
    """Test ParserSettings with custom values."""
    settings = ParserSettings(
        preserveBNodeIds=True,
        failOnUnknownDataTypes=True,
        verifyDataTypeValues=True,
        normalizeDataTypeValues=True,
        failOnUnknownLanguageTags=True,
        verifyLanguageTags=False,
        normalizeLanguageTags=True,
        stopOnError=False,
        contextLink="http://example.org/context",
    )

    assert settings.preserveBNodeIds is True
    assert settings.failOnUnknownDataTypes is True
    assert settings.verifyDataTypeValues is True
    assert settings.normalizeDataTypeValues is True
    assert settings.failOnUnknownLanguageTags is True
    assert settings.verifyLanguageTags is False
    assert settings.normalizeLanguageTags is True
    assert settings.stopOnError is False
    assert settings.contextLink == "http://example.org/context"


@pytest.mark.parametrize(
    "field_name,field_value",
    [
        ("preserveBNodeIds", "true"),
        ("preserveBNodeIds", 1),
        ("preserveBNodeIds", None),
        ("failOnUnknownDataTypes", "false"),
        ("failOnUnknownDataTypes", 0),
        ("failOnUnknownDataTypes", []),
        ("verifyDataTypeValues", "True"),
        ("verifyDataTypeValues", {}),
        ("normalizeDataTypeValues", "yes"),
        ("normalizeDataTypeValues", 1.0),
        ("failOnUnknownLanguageTags", "no"),
        ("failOnUnknownLanguageTags", None),
        ("verifyLanguageTags", "1"),
        ("verifyLanguageTags", object()),
        ("normalizeLanguageTags", "true"),
        ("normalizeLanguageTags", 0),
        ("stopOnError", "false"),
        ("stopOnError", None),
    ],
)
def test_parser_settings_invalid_boolean_fields(field_name, field_value):
    """Test that invalid boolean field types raise ValueError."""
    kwargs = {field_name: field_value}
    with pytest.raises(ValueError):
        ParserSettings(**kwargs)


def test_parser_settings_as_dict():
    """Test ParserSettings.as_dict() serialization."""
    settings = ParserSettings(
        preserveBNodeIds=True,
        failOnUnknownDataTypes=False,
        contextLink="http://example.org/context",
    )

    result = settings.as_dict()

    assert isinstance(result, dict)
    assert result["preserveBNodeIds"] is True
    assert result["failOnUnknownDataTypes"] is False
    assert result["verifyDataTypeValues"] is False
    assert result["normalizeDataTypeValues"] is False
    assert result["failOnUnknownLanguageTags"] is False
    assert result["verifyLanguageTags"] is True
    assert result["normalizeLanguageTags"] is False
    assert result["stopOnError"] is True
    assert result["contextLink"] == "http://example.org/context"


def test_parser_settings_frozen():
    """Test that ParserSettings is immutable."""
    settings = ParserSettings()
    with pytest.raises(AttributeError):
        settings.preserveBNodeIds = True


# ==================== ImportSettings Tests ====================


def test_import_settings_valid():
    """Test creating a valid ImportSettings with all fields."""
    parser_settings = ParserSettings(preserveBNodeIds=True)
    settings = ImportSettings(
        name="test-file.ttl",
        status="PENDING",
        message="Waiting in queue",
        size="1.5 MB",
        lastModified=1704067200,
        imported=1704067200,
        addedStatements=100,
        removedStatements=10,
        numReplacedGraphs=2,
        context="http://example.org/graph",
        replaceGraphs=["http://example.org/old-graph"],
        baseURI="http://example.org/",
        forceSerial=True,
        type="file",
        format="text/turtle",
        data=None,
        parserSettings=parser_settings,
    )

    assert settings.name == "test-file.ttl"
    assert settings.status == "PENDING"
    assert settings.message == "Waiting in queue"
    assert settings.size == "1.5 MB"
    assert settings.lastModified == 1704067200
    assert settings.imported == 1704067200
    assert settings.addedStatements == 100
    assert settings.removedStatements == 10
    assert settings.numReplacedGraphs == 2
    assert settings.context == "http://example.org/graph"
    assert settings.replaceGraphs == ["http://example.org/old-graph"]
    assert settings.baseURI == "http://example.org/"
    assert settings.forceSerial is True
    assert settings.type == "file"
    assert settings.format == "text/turtle"
    assert settings.data is None
    assert settings.parserSettings == parser_settings


def test_import_settings_minimal():
    """Test creating ImportSettings with only required fields."""
    settings = ImportSettings(
        name="test-file.ttl",
        status="DONE",
        size="1024",
        lastModified=1704067200,
        imported=1704067200,
        addedStatements=50,
        removedStatements=0,
        numReplacedGraphs=0,
    )

    assert settings.name == "test-file.ttl"
    assert settings.status == "DONE"
    assert settings.message == ""
    assert settings.size == "1024"
    assert settings.lastModified == 1704067200
    assert settings.imported == 1704067200
    assert settings.addedStatements == 50
    assert settings.removedStatements == 0
    assert settings.numReplacedGraphs == 0
    assert settings.context is None
    assert settings.replaceGraphs == []
    assert settings.baseURI is None
    assert settings.forceSerial is False
    assert settings.type == "file"
    assert settings.format is None
    assert settings.data is None
    assert isinstance(settings.parserSettings, ParserSettings)


@pytest.mark.parametrize(
    "status",
    ["PENDING", "IMPORTING", "DONE", "ERROR", "NONE", "INTERRUPTING"],
)
def test_import_settings_valid_status_values(status):
    """Test that all valid status values are accepted."""
    settings = ImportSettings(
        name="test.ttl",
        status=status,
        size="1KB",
        lastModified=1704067200,
        imported=1704067200,
        addedStatements=0,
        removedStatements=0,
        numReplacedGraphs=0,
    )
    assert settings.status == status


@pytest.mark.parametrize(
    "status",
    ["pending", "RUNNING", "COMPLETED", "FAILED", "UNKNOWN", "", None, 123],
)
def test_import_settings_invalid_status_values(status):
    """Test that invalid status values raise ValueError."""
    with pytest.raises(ValueError):
        ImportSettings(
            name="test.ttl",
            status=status,
            size="1KB",
            lastModified=1704067200,
            imported=1704067200,
            addedStatements=0,
            removedStatements=0,
            numReplacedGraphs=0,
        )


@pytest.mark.parametrize(
    "name",
    [123, None, [], {}],
)
def test_import_settings_invalid_name(name):
    """Test that invalid name types raise ValueError."""
    with pytest.raises(ValueError):
        ImportSettings(
            name=name,
            status="PENDING",
            size="1KB",
            lastModified=1704067200,
            imported=1704067200,
            addedStatements=0,
            removedStatements=0,
            numReplacedGraphs=0,
        )


@pytest.mark.parametrize(
    "message",
    [123, None, [], {}],
)
def test_import_settings_invalid_message(message):
    """Test that invalid message types raise ValueError."""
    with pytest.raises(ValueError):
        ImportSettings(
            name="test.ttl",
            status="PENDING",
            message=message,
            size="1KB",
            lastModified=1704067200,
            imported=1704067200,
            addedStatements=0,
            removedStatements=0,
            numReplacedGraphs=0,
        )


@pytest.mark.parametrize(
    "size",
    [123, None, [], {}],
)
def test_import_settings_invalid_size(size):
    """Test that invalid size types raise ValueError."""
    with pytest.raises(ValueError):
        ImportSettings(
            name="test.ttl",
            status="PENDING",
            size=size,
            lastModified=1704067200,
            imported=1704067200,
            addedStatements=0,
            removedStatements=0,
            numReplacedGraphs=0,
        )


@pytest.mark.parametrize(
    "last_modified",
    ["123", None, [], {}, 1.5],
)
def test_import_settings_invalid_last_modified(last_modified):
    """Test that invalid lastModified types raise ValueError."""
    with pytest.raises(ValueError):
        ImportSettings(
            name="test.ttl",
            status="PENDING",
            size="1KB",
            lastModified=last_modified,
            imported=1704067200,
            addedStatements=0,
            removedStatements=0,
            numReplacedGraphs=0,
        )


@pytest.mark.parametrize(
    "imported",
    ["123", None, [], {}, 1.5],
)
def test_import_settings_invalid_imported(imported):
    """Test that invalid imported types raise ValueError."""
    with pytest.raises(ValueError):
        ImportSettings(
            name="test.ttl",
            status="PENDING",
            size="1KB",
            lastModified=1704067200,
            imported=imported,
            addedStatements=0,
            removedStatements=0,
            numReplacedGraphs=0,
        )


@pytest.mark.parametrize(
    "added_statements",
    ["100", None, [], {}, 1.5],
)
def test_import_settings_invalid_added_statements(added_statements):
    """Test that invalid addedStatements types raise ValueError."""
    with pytest.raises(ValueError):
        ImportSettings(
            name="test.ttl",
            status="PENDING",
            size="1KB",
            lastModified=1704067200,
            imported=1704067200,
            addedStatements=added_statements,
            removedStatements=0,
            numReplacedGraphs=0,
        )


@pytest.mark.parametrize(
    "removed_statements",
    ["10", None, [], {}, 1.5],
)
def test_import_settings_invalid_removed_statements(removed_statements):
    """Test that invalid removedStatements types raise ValueError."""
    with pytest.raises(ValueError):
        ImportSettings(
            name="test.ttl",
            status="PENDING",
            size="1KB",
            lastModified=1704067200,
            imported=1704067200,
            addedStatements=0,
            removedStatements=removed_statements,
            numReplacedGraphs=0,
        )


@pytest.mark.parametrize(
    "num_replaced_graphs",
    ["0", None, [], {}, 1.5],
)
def test_import_settings_invalid_num_replaced_graphs(num_replaced_graphs):
    """Test that invalid numReplacedGraphs types raise ValueError."""
    with pytest.raises(ValueError):
        ImportSettings(
            name="test.ttl",
            status="PENDING",
            size="1KB",
            lastModified=1704067200,
            imported=1704067200,
            addedStatements=0,
            removedStatements=0,
            numReplacedGraphs=num_replaced_graphs,
        )


@pytest.mark.parametrize(
    "replace_graphs",
    ["graph", {"graph": True}, 123],
)
def test_import_settings_invalid_replace_graphs(replace_graphs):
    """Test that invalid replaceGraphs types raise ValueError."""
    with pytest.raises(ValueError):
        ImportSettings(
            name="test.ttl",
            status="PENDING",
            size="1KB",
            lastModified=1704067200,
            imported=1704067200,
            addedStatements=0,
            removedStatements=0,
            numReplacedGraphs=0,
            replaceGraphs=replace_graphs,
        )


@pytest.mark.parametrize(
    "force_serial",
    ["true", 1, None, [], {}],
)
def test_import_settings_invalid_force_serial(force_serial):
    """Test that invalid forceSerial types raise ValueError."""
    with pytest.raises(ValueError):
        ImportSettings(
            name="test.ttl",
            status="PENDING",
            size="1KB",
            lastModified=1704067200,
            imported=1704067200,
            addedStatements=0,
            removedStatements=0,
            numReplacedGraphs=0,
            forceSerial=force_serial,
        )


@pytest.mark.parametrize(
    "type_",
    [123, None, [], {}],
)
def test_import_settings_invalid_type(type_):
    """Test that invalid type types raise ValueError."""
    with pytest.raises(ValueError):
        ImportSettings(
            name="test.ttl",
            status="PENDING",
            size="1KB",
            lastModified=1704067200,
            imported=1704067200,
            addedStatements=0,
            removedStatements=0,
            numReplacedGraphs=0,
            type=type_,
        )


def test_import_settings_invalid_parser_settings():
    """Test that invalid parserSettings type raises ValueError."""
    with pytest.raises(ValueError):
        ImportSettings(
            name="test.ttl",
            status="PENDING",
            size="1KB",
            lastModified=1704067200,
            imported=1704067200,
            addedStatements=0,
            removedStatements=0,
            numReplacedGraphs=0,
            parserSettings={"preserveBNodeIds": True},
        )


def test_import_settings_as_dict():
    """Test ImportSettings.as_dict() serialization."""
    parser_settings = ParserSettings(preserveBNodeIds=True)
    settings = ImportSettings(
        name="test.ttl",
        status="DONE",
        message="Import complete",
        size="2.5 MB",
        lastModified=1704067200,
        imported=1704067201,
        addedStatements=500,
        removedStatements=50,
        numReplacedGraphs=1,
        context="http://example.org/graph",
        replaceGraphs=["http://example.org/old"],
        baseURI="http://example.org/",
        forceSerial=True,
        type="file",
        format="text/turtle",
        data=None,
        parserSettings=parser_settings,
    )

    result = settings.as_dict()

    assert isinstance(result, dict)
    assert result["name"] == "test.ttl"
    assert result["status"] == "DONE"
    assert result["message"] == "Import complete"
    assert result["size"] == "2.5 MB"
    assert result["lastModified"] == 1704067200
    assert result["imported"] == 1704067201
    assert result["addedStatements"] == 500
    assert result["removedStatements"] == 50
    assert result["numReplacedGraphs"] == 1
    assert result["context"] == "http://example.org/graph"
    assert result["replaceGraphs"] == ["http://example.org/old"]
    assert result["baseURI"] == "http://example.org/"
    assert result["forceSerial"] is True
    assert result["type"] == "file"
    assert result["format"] == "text/turtle"
    assert result["data"] is None
    assert isinstance(result["parserSettings"], dict)
    assert result["parserSettings"]["preserveBNodeIds"] is True


def test_import_settings_frozen():
    """Test that ImportSettings is immutable."""
    settings = ImportSettings(
        name="test.ttl",
        status="PENDING",
        size="1KB",
        lastModified=1704067200,
        imported=1704067200,
        addedStatements=0,
        removedStatements=0,
        numReplacedGraphs=0,
    )
    with pytest.raises(AttributeError):
        settings.name = "other.ttl"


def test_import_settings_as_dict_json_serializable():
    """Test that ImportSettings.as_dict() result is JSON serializable."""
    import json

    settings = ImportSettings(
        name="test.ttl",
        status="DONE",
        size="1KB",
        lastModified=1704067200,
        imported=1704067200,
        addedStatements=100,
        removedStatements=10,
        numReplacedGraphs=0,
        parserSettings=ParserSettings(preserveBNodeIds=True),
    )

    result = settings.as_dict()

    # Should be able to serialize to JSON without errors
    json_str = json.dumps(result)
    assert isinstance(json_str, str)

    # Should be able to deserialize back
    deserialized = json.loads(json_str)
    assert deserialized == result


# ==================== ServerImportBody Tests ====================


def test_server_import_body_valid():
    """Test creating a valid ServerImportBody with all fields."""
    import_settings = ImportSettings(
        name="test-file.ttl",
        status="PENDING",
        size="1.5 MB",
        lastModified=1704067200,
        imported=1704067200,
        addedStatements=100,
        removedStatements=10,
        numReplacedGraphs=2,
    )
    body = ServerImportBody(
        importSettings=import_settings,
        fileNames=["file1.ttl", "file2.ttl"],
    )

    assert body.importSettings == import_settings
    assert body.fileNames == ["file1.ttl", "file2.ttl"]


def test_server_import_body_import_settings_optional():
    """Test creating a ServerImportBody without importSettings."""
    body = ServerImportBody(fileNames=["file1.ttl", "file2.ttl"])

    assert body.importSettings is None
    assert body.fileNames == ["file1.ttl", "file2.ttl"]


def test_server_import_body_empty_file_names():
    """Test creating a ServerImportBody with an empty fileNames list."""
    import_settings = ImportSettings(
        name="test-file.ttl",
        status="DONE",
        size="1KB",
        lastModified=1704067200,
        imported=1704067200,
        addedStatements=0,
        removedStatements=0,
        numReplacedGraphs=0,
    )
    body = ServerImportBody(
        importSettings=import_settings,
        fileNames=[],
    )

    assert body.importSettings == import_settings
    assert body.fileNames == []


def test_server_import_body_frozen():
    """Test that ServerImportBody is immutable."""
    import_settings = ImportSettings(
        name="test-file.ttl",
        status="PENDING",
        size="1KB",
        lastModified=1704067200,
        imported=1704067200,
        addedStatements=0,
        removedStatements=0,
        numReplacedGraphs=0,
    )
    body = ServerImportBody(
        importSettings=import_settings,
        fileNames=["file.ttl"],
    )
    with pytest.raises(AttributeError):
        body.fileNames = ["other.ttl"]


@pytest.mark.parametrize(
    "import_settings",
    [
        {"name": "test.ttl", "status": "PENDING"},
        "not-a-settings-object",
        123,
        [],
    ],
)
def test_server_import_body_invalid_import_settings(import_settings):
    """Test that invalid importSettings types raise ValueError."""
    with pytest.raises(ValueError):
        ServerImportBody(
            importSettings=import_settings,
            fileNames=["file.ttl"],
        )


@pytest.mark.parametrize(
    "file_names",
    [
        "file.ttl",
        {"file.ttl": True},
        123,
        None,
    ],
)
def test_server_import_body_invalid_file_names_type(file_names):
    """Test that invalid fileNames types raise ValueError."""
    import_settings = ImportSettings(
        name="test-file.ttl",
        status="PENDING",
        size="1KB",
        lastModified=1704067200,
        imported=1704067200,
        addedStatements=0,
        removedStatements=0,
        numReplacedGraphs=0,
    )
    with pytest.raises(ValueError):
        ServerImportBody(
            importSettings=import_settings,
            fileNames=file_names,
        )


@pytest.mark.parametrize(
    "file_names",
    [
        ["file.ttl", 123],
        [1, 2, 3],
        ["file.ttl", None],
        ["file.ttl", []],
    ],
)
def test_server_import_body_invalid_file_names_elements(file_names):
    """Test that non-string elements in fileNames raise ValueError."""
    import_settings = ImportSettings(
        name="test-file.ttl",
        status="PENDING",
        size="1KB",
        lastModified=1704067200,
        imported=1704067200,
        addedStatements=0,
        removedStatements=0,
        numReplacedGraphs=0,
    )
    with pytest.raises(ValueError):
        ServerImportBody(
            importSettings=import_settings,
            fileNames=file_names,
        )


def test_server_import_body_as_dict():
    """Test ServerImportBody.as_dict() serialization."""
    parser_settings = ParserSettings(preserveBNodeIds=True)
    import_settings = ImportSettings(
        name="test.ttl",
        status="DONE",
        message="Import complete",
        size="2.5 MB",
        lastModified=1704067200,
        imported=1704067201,
        addedStatements=500,
        removedStatements=50,
        numReplacedGraphs=1,
        parserSettings=parser_settings,
    )
    body = ServerImportBody(
        importSettings=import_settings,
        fileNames=["file1.ttl", "file2.ttl"],
    )

    result = body.as_dict()

    assert isinstance(result, dict)
    assert "importSettings" in result
    assert "fileNames" in result
    assert isinstance(result["importSettings"], dict)
    assert result["importSettings"]["name"] == "test.ttl"
    assert result["importSettings"]["status"] == "DONE"
    assert result["fileNames"] == ["file1.ttl", "file2.ttl"]


def test_server_import_body_as_dict_omits_none_import_settings():
    """Test that ServerImportBody.as_dict() omits importSettings when None."""
    body = ServerImportBody(fileNames=["file1.ttl", "file2.ttl"])

    result = body.as_dict()

    assert isinstance(result, dict)
    assert "importSettings" not in result
    assert result["fileNames"] == ["file1.ttl", "file2.ttl"]


def test_server_import_body_as_dict_json_serializable():
    """Test that ServerImportBody.as_dict() result is JSON serializable."""
    import json

    import_settings = ImportSettings(
        name="test.ttl",
        status="DONE",
        size="1KB",
        lastModified=1704067200,
        imported=1704067200,
        addedStatements=100,
        removedStatements=10,
        numReplacedGraphs=0,
    )
    body = ServerImportBody(
        importSettings=import_settings,
        fileNames=["file.ttl"],
    )

    result = body.as_dict()

    # Should be able to serialize to JSON without errors
    json_str = json.dumps(result)
    assert isinstance(json_str, str)

    # Should be able to deserialize back
    deserialized = json.loads(json_str)
    assert deserialized == result
