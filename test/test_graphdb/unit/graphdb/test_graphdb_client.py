from __future__ import annotations

from rdflib.contrib.graphdb import GraphDBClient
from rdflib.contrib.graphdb.client import GraphDB, RepositoryManager


def test_client_has_graphdb_repository_manager(client: GraphDBClient):
    assert client.repository_manager_cls == RepositoryManager


def test_client_has_graphdb_rest_client(client: GraphDBClient):
    assert isinstance(client.graphdb, GraphDB)
