import pytest
from testcontainers.core.container import DockerContainer

from rdflib.contrib.graphdb import GraphDBClient
from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping rdf4j tests, httpx not available"
)


@pytest.fixture(scope="function")
def client(graphdb_container: DockerContainer):
    port = graphdb_container.get_exposed_port(7200)
    with GraphDBClient(f"http://localhost:{port}/", auth=("admin", "admin")) as client:
        yield client
