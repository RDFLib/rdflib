from __future__ import annotations

import pathlib
import uuid

import pytest

from rdflib import SH, Graph, Literal, URIRef
from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping rdf4j tests, httpx not available"
)

if has_httpx:
    from rdflib.contrib.graphdb import GraphDBClient
    from rdflib.contrib.graphdb.exceptions import RepositoryNotFoundError
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


@pytest.mark.testcontainer
def test_graphdb_repository_create_json(client: GraphDBClient):
    """Create a repository via JSON config and verify it exists."""
    base_config = client.repos.get("test-repo")
    repo_id = f"test-repo-create-json-{uuid.uuid4().hex[:8]}"
    new_config = RepositoryConfigBeanCreate(
        id=repo_id,
        title=f"Repo {repo_id}",
        type=base_config.type,
        sesameType=base_config.sesameType,
        location=base_config.location,
        params=base_config.params,
    )

    try:
        client.repos.create(new_config)
        created = client.repos.get(repo_id)
        assert isinstance(created, RepositoryConfigBean)
        assert created.id == repo_id
    finally:
        try:
            client.repos.delete(repo_id)
        except RepositoryNotFoundError:
            pass


@pytest.mark.testcontainer
def test_graphdb_repository_create_multipart(client: GraphDBClient):
    """Create a repository via multipart Turtle config (with an extra file) and verify it exists."""
    repo_id = f"test-repo-create-ttl-{uuid.uuid4().hex[:8]}"
    config_path = (
        pathlib.Path(__file__).parent.parent
        / "repo-configs"
        / "test-graphdb-repo-config.ttl"
    )
    ttl_config = config_path.read_text().replace("test-repo", repo_id)

    try:
        client.repos.create(ttl_config, files={"obdaFile": b"obda-bytes"})
        created = client.repos.get(repo_id)
        assert isinstance(created, RepositoryConfigBean)
        assert created.id == repo_id
    finally:
        try:
            client.repos.delete(repo_id)
        except RepositoryNotFoundError:
            pass


@pytest.mark.testcontainer
def test_graphdb_repository_delete(client: GraphDBClient):
    """Test deleting a repository configuration."""
    repo_id = "test-repo"
    client.repos.delete(repo_id)
    with pytest.raises(RepositoryNotFoundError):
        client.repos.get(repo_id)


@pytest.mark.testcontainer
def test_graphdb_repository_list(client: GraphDBClient):
    """Test listing repository configurations."""
    repos = client.repos.list()
    identifiers = {repo.id for repo in repos}
    assert "test-repo" in identifiers


@pytest.mark.testcontainer
def test_graphdb_repository_validate_reports(client: GraphDBClient):
    """Validate repository data with SHACL shapes and inspect conform/non-conform reports."""
    repo = client.repositories.get("test-repo")
    data_path = pathlib.Path(__file__).parent.parent.parent / "data" / "quads-1.nq"
    with open(data_path, "rb") as file:
        repo.overwrite(file)

    iri_shape = """
        PREFIX sh: <http://www.w3.org/ns/shacl#>
        PREFIX ex: <http://example.org/>

        ex:PObjectIriShape a sh:NodeShape ;
        sh:targetSubjectsOf ex:p ;
        sh:property [
            sh:path ex:p ;
            sh:nodeKind sh:IRI ;
        ] .
    """
    iri_report_text = client.repos.validate(
        "test-repo", content_type="text/turtle", content=iri_shape
    )
    iri_report_graph = Graph().parse(data=iri_report_text, format="turtle")
    iri_conforms: list[Literal | URIRef] = [
        value
        for value in iri_report_graph.objects(None, SH.conforms)
        if isinstance(value, (Literal, URIRef))
    ]
    assert iri_conforms and any(val.toPython() is True for val in iri_conforms)

    literal_shape = """
        PREFIX sh: <http://www.w3.org/ns/shacl#>
        PREFIX ex: <http://example.org/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        ex:PObjectLiteralShape a sh:NodeShape ;
        sh:targetSubjectsOf ex:p ;
        sh:property [
            sh:path ex:p ;
            sh:datatype xsd:string ;
        ] .
    """
    literal_report_text = client.repos.validate(
        "test-repo", content_type="text/turtle", content=literal_shape
    )
    literal_report_graph = Graph().parse(data=literal_report_text, format="turtle")
    literal_conforms: list[Literal | URIRef] = [
        value
        for value in literal_report_graph.objects(None, SH.conforms)
        if isinstance(value, (Literal, URIRef))
    ]
    assert literal_conforms and any(val.toPython() is False for val in literal_conforms)
