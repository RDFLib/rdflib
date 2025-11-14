import pathlib

import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.image import DockerImage
from testcontainers.core.waiting_utils import wait_for_logs

from rdflib import Dataset
from rdflib.contrib.rdf4j import has_httpx
from rdflib.contrib.rdf4j.exceptions import RepositoryNotFoundError
from rdflib.namespace import NamespaceManager
from rdflib.plugins.stores.rdf4j import RDF4JStore

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping rdf4j tests, httpx not available"
)

if has_httpx:
    from rdflib.contrib.rdf4j import RDF4JClient

    GRAPHDB_PORT = 7200

    @pytest.fixture(scope="package")
    def graphdb_container():
        with DockerImage(str(pathlib.Path(__file__).parent / "docker")) as image:
            container = DockerContainer(str(image))
            container.with_exposed_ports(GRAPHDB_PORT)
            container.start()
            wait_for_logs(container, "Started GraphDB")
            yield container
            container.stop()

    @pytest.fixture(scope="function")
    def client(graphdb_container: DockerContainer):
        port = graphdb_container.get_exposed_port(7200)
        with RDF4JClient(
            f"http://localhost:{port}/", auth=("admin", "admin")
        ) as client:
            yield client
            try:
                client.repositories.delete("test-repo")
            except RepositoryNotFoundError:
                pass

    @pytest.fixture(scope="function")
    def repo(client: RDF4JClient):
        config_path = (
            pathlib.Path(__file__).parent / "repo-configs/test-repo-config.ttl"
        )
        with open(config_path) as file:
            config = file.read()

        repo = client.repositories.create("test-repo", config)
        assert repo.identifier == "test-repo"
        yield repo
        client.repositories.delete("test-repo")

    @pytest.fixture(scope="function")
    def ds(graphdb_container: DockerContainer):
        port = graphdb_container.get_exposed_port(7200)
        store = RDF4JStore(
            f"http://localhost:{port}/",
            "test-repo",
            auth=("admin", "admin"),
            create=True,
        )
        ds = Dataset(store)
        ds.namespace_manager = NamespaceManager(ds, "none")
        yield ds
        ds.store.client.repositories.delete("test-repo")
        ds.close()
