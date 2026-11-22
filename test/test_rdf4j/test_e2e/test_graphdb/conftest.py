from importlib.util import find_spec

import pytest

from rdflib.contrib.rdf4j import has_httpx
from rdflib.contrib.rdf4j.exceptions import RepositoryNotFoundError

has_testcontainers = find_spec("testcontainers") is not None

pytestmark = pytest.mark.skipif(
    not (has_httpx and has_testcontainers),
    reason="skipping rdf4j tests, httpx or testcontainers not available",
)

if has_httpx and has_testcontainers:
    from testcontainers.core.container import DockerContainer

    from rdflib.contrib.graphdb import GraphDBClient

    @pytest.fixture(scope="function")
    def client(graphdb_container: DockerContainer):
        port = graphdb_container.get_exposed_port(7200)
        with GraphDBClient(
            f"http://localhost:{port}/", auth=("admin", "admin")
        ) as client:
            yield client
            try:
                client.repositories.delete("test-repo")
            except (RepositoryNotFoundError, RuntimeError):
                pass
