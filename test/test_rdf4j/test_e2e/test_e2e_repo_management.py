import pathlib

import pytest

from rdflib import BNode, Dataset, URIRef
from rdflib.compare import isomorphic
from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping rdf4j tests, httpx not available"
)

if has_httpx:
    import httpx
    from rdflib.contrib.rdf4j import RDF4JClient
    from rdflib.contrib.rdf4j.client import Repository
    from rdflib.contrib.rdf4j.exceptions import (
        RepositoryAlreadyExistsError,
        RepositoryFormatError,
        RepositoryNotFoundError,
        RepositoryNotHealthyError,
    )


@pytest.mark.testcontainer
def test_repos(client: RDF4JClient):
    assert client.repositories.list() == []


@pytest.mark.testcontainer
def test_list_repo_non_existent(client: RDF4JClient):
    assert client.repositories.list() == []
    with pytest.raises(RepositoryNotFoundError):
        assert client.repositories.get("non-existent") is None


@pytest.mark.testcontainer
def test_list_repo_format_error(client: RDF4JClient, monkeypatch):
    class MockResponse:
        def json(self):
            return {}

        def raise_for_status(self):
            pass

    monkeypatch.setattr(httpx.Client, "get", lambda *args, **kwargs: MockResponse())
    with pytest.raises(RepositoryFormatError):
        client.repositories.list()


@pytest.mark.testcontainer
def test_repo_manager_crud(client: RDF4JClient):
    # Empty state
    assert client.repositories.list() == []

    config_path = pathlib.Path(__file__).parent / "repo-configs/test-repo-config.ttl"
    with open(config_path) as file:
        config = file.read()

    repo = client.repositories.create("test-repo", config)
    assert repo.identifier == "test-repo"
    assert repo.health()

    # New repository created
    assert len(client.repositories.list()) == 1

    # Repo already exists error
    with pytest.raises(RepositoryAlreadyExistsError):
        client.repositories.create("test-repo", config)

    # Confirm repo is empty
    assert repo.size() == 0
    ds = repo.get()
    assert isinstance(ds, Dataset)
    assert len(ds) == 0

    # Use the overwrite method to add statements to the repo
    with open(pathlib.Path(__file__).parent.parent / "data/quads-2.nq", "rb") as file:
        repo.overwrite(file)
    assert repo.size() == 1
    graphs = repo.graph_names()
    assert len(graphs) == 1
    assert any(value in graphs for value in [URIRef("urn:graph:a3")])
    ds = repo.get()
    assert len(ds) == 1
    str_result = ds.serialize(format="nquads")
    assert (
        "<http://example.org/s3> <http://example.org/p3> <http://example.org/o3> <urn:graph:a3> ."
        in str_result
    )

    # Overwrite with a different file.
    with open(pathlib.Path(__file__).parent.parent / "data/quads-1.nq", "rb") as file:
        repo.overwrite(file)
    assert repo.size() == 2
    ds = repo.get()
    assert len(ds) == 2
    graphs = repo.graph_names()
    assert len(graphs) == 2
    assert any(
        value in graphs for value in [URIRef("urn:graph:a"), URIRef("urn:graph:b")]
    )
    str_result = ds.serialize(format="nquads")
    assert (
        "<http://example.org/s> <http://example.org/p> <http://example.org/o> <urn:graph:a> ."
        in str_result
    )
    assert (
        "<http://example.org/s2> <http://example.org/p2> <http://example.org/o2> <urn:graph:b> ."
        in str_result
    )

    # Get statements using a filter pattern
    ds = repo.get(subj=URIRef("http://example.org/s2"))
    assert len(ds) == 1
    str_result = ds.serialize(format="nquads")
    assert (
        "<http://example.org/s2> <http://example.org/p2> <http://example.org/o2> <urn:graph:b> ."
        in str_result
    )

    # Use the delete method to delete a statement using a filter pattern
    repo.delete(subj=URIRef("http://example.org/s"))
    assert repo.size() == 1
    ds = repo.get()
    assert len(ds) == 1
    str_result = ds.serialize(format="nquads")
    assert (
        "<http://example.org/s2> <http://example.org/p2> <http://example.org/o2> <urn:graph:b> ."
        in str_result
    )

    # Append to the repository a new RDF payload with blank node graph names
    with open(pathlib.Path(__file__).parent.parent / "data/quads-3.nq", "rb") as file:
        repo.upload(file)
    assert repo.size() == 2
    ds = repo.get()
    assert len(ds) == 2
    graphs = repo.graph_names()
    assert len(graphs) == 2
    assert any(
        value in graphs
        for value in [URIRef("urn:graph:a"), URIRef("urn:graph:b"), BNode("c")]
    )
    data = """
    <http://example.org/s2> <http://example.org/p2> <http://example.org/o2> <urn:graph:b> .
    _:b-test <http://example.org/p> _:c _:graph .
    """
    ds2 = Dataset().parse(data=data, format="nquads")
    assert isinstance(ds, Dataset)
    for graph in ds.graphs():
        assert any(isomorphic(graph, graph2) for graph2 in ds2.graphs())

    # Delete repository
    client.repositories.delete("test-repo")
    assert client.repositories.list() == []

    # Deleting non-existent repo
    with pytest.raises(RepositoryNotFoundError):
        client.repositories.delete("test-repo")


@pytest.mark.testcontainer
def test_repo_not_healthy(repo: Repository, monkeypatch: pytest.MonkeyPatch):
    class MockResponse:
        def raise_for_status(self):
            raise httpx.HTTPStatusError(
                "",
                request=httpx.Request("post", ""),
                response=httpx.Response(status_code=500),
            )

    monkeypatch.setattr(httpx.Client, "post", lambda *args, **kwargs: MockResponse())
    with pytest.raises(RepositoryNotHealthyError):
        repo.health()
