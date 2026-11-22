from __future__ import annotations

import pytest

from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    from rdflib.contrib.graphdb.models import (
        GraphDBRepository,
        OWLimParameter,
        RepositoryConfigBeanCreate,
        RepositoryState,
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


def test_graphdb_repository_from_dict_does_not_mutate_input():
    """from_dict should not mutate the input mapping."""
    data = {
        "id": "repo2",
        "state": "RUNNING",
    }
    expected = dict(data)

    repo = GraphDBRepository.from_dict(data)

    assert repo.state == RepositoryState.RUNNING
    assert data == expected


def test_graphdb_repository_from_dict_invalid_state():
    """Test that from_dict raises ValueError for invalid state values."""
    data = {
        "id": "repo3",
        "state": "INVALID_STATE",
    }

    with pytest.raises(ValueError):
        GraphDBRepository.from_dict(data)


def test_graphdb_repository_from_dict_unexpected_key():
    """Test that from_dict raises TypeError for unexpected keys."""
    data = {
        "id": "repo4",
        "unexpected_field": "some_value",
    }

    with pytest.raises(TypeError):
        GraphDBRepository.from_dict(data)
