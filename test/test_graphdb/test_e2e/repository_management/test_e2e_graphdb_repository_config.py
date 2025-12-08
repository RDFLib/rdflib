from __future__ import annotations

import pytest

from rdflib import Graph, Literal, URIRef
from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping rdf4j tests, httpx not available"
)

if has_httpx:
    from rdflib.contrib.graphdb import GraphDBClient
    from rdflib.contrib.graphdb.models import (
        RepositoryConfigBean,
        RepositoryConfigBeanCreate,
    )


@pytest.mark.testcontainer
def test_graphdb_repository_get_config(client: GraphDBClient):
    config = client.repos.get("test-repo")
    assert isinstance(config, RepositoryConfigBean)
    assert config.id == "test-repo"


@pytest.mark.testcontainer
def test_graph_repository_get_config_graph(client: GraphDBClient):
    config_graph = client.repos.get("test-repo", content_type="text/turtle")
    assert isinstance(config_graph, Graph)
    assert len(config_graph)
    predicate_object_values = set(config_graph.predicate_objects(unique=True))
    assert (
        URIRef("http://www.openrdf.org/config/repository#repositoryID"),
        Literal("test-repo"),
    ) in predicate_object_values


@pytest.mark.testcontainer
def test_graphdb_repository_edit_config(client: GraphDBClient):
    """Test editing a repository configuration."""
    # Get the current config
    original_config = client.repos.get("test-repo")
    assert isinstance(original_config, RepositoryConfigBean)
    assert original_config.id == "test-repo"

    # Create a modified config with a new title
    new_title = "Updated Test Repository"
    updated_config = RepositoryConfigBeanCreate(
        id=original_config.id,
        title=new_title,
        type=original_config.type,
        sesameType=original_config.sesameType,
        location=original_config.location,
        params=original_config.params,
    )

    # Edit the repository configuration
    client.repos.edit("test-repo", updated_config)

    # Verify the change was applied
    modified_config = client.repos.get("test-repo")
    assert isinstance(modified_config, RepositoryConfigBean)
    assert modified_config.id == "test-repo"
    assert modified_config.title == new_title
    assert modified_config.type == original_config.type
    assert modified_config.sesameType == original_config.sesameType
    assert modified_config.location == original_config.location
