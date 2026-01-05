import pathlib
from importlib.util import find_spec

import pytest

from rdflib.contrib.rdf4j import has_httpx
from rdflib.contrib.rdf4j.exceptions import RepositoryNotFoundError

has_testcontainers = find_spec("testcontainers") is not None

pytestmark = pytest.mark.skipif(
    not (has_httpx and has_testcontainers),
    reason="skipping graphdb tests, httpx or testcontainers is not available",
)

if has_httpx and has_testcontainers:
    from testcontainers.core.container import DockerContainer
    from testcontainers.core.image import DockerImage
    from testcontainers.core.waiting_utils import wait_for_logs

    from rdflib.contrib.graphdb import GraphDBClient

    GRAPHDB_PORT = 7200

    @pytest.fixture(scope="package")
    def graphdb_container():
        with DockerImage(str(pathlib.Path(__file__).parent / "docker")) as image:
            container = DockerContainer(str(image))
            container.with_exposed_ports(GRAPHDB_PORT)
            # Mount test data directory to GraphDB import server import files location
            test_data_dir = str(pathlib.Path(__file__).parent.parent / "data")
            container.with_volume_mapping(test_data_dir, "/root/graphdb-import")
            container.start()
            wait_for_logs(container, "Started GraphDB")
            yield container
            container.stop()

    @pytest.fixture(scope="function")
    def client(graphdb_container: DockerContainer):
        port = graphdb_container.get_exposed_port(7200)
        with GraphDBClient(
            f"http://localhost:{port}/", auth=("admin", "admin")
        ) as client:
            config_path = (
                pathlib.Path(__file__).parent
                / "repo-configs/test-graphdb-repo-config.ttl"
            )
            with open(config_path) as file:
                config = file.read()

            repo = client.repositories.create("test-repo", config)
            assert repo.identifier == "test-repo"
            yield client
            try:
                client.repositories.delete("test-repo")
            except (RepositoryNotFoundError, RuntimeError):
                pass
