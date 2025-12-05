from __future__ import annotations

import pytest

from rdflib import Graph, Literal, URIRef
from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping rdf4j tests, httpx not available"
)

if has_httpx:
    from rdflib.contrib.graphdb import GraphDBClient
    from rdflib.contrib.graphdb.models import RepositoryConfigBean


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
