import pathlib

import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.image import DockerImage
from testcontainers.core.waiting_utils import wait_for_logs

from rdflib.contrib.rdf4j import RDF4JClient

RDF4J_IMAGE = "eclipse/rdf4j-workbench:5.1.6-jetty"
RDF4J_PORT = 8080
GRAPHDB_PORT = 7200


@pytest.fixture(scope="function")
def rdf4j_container():
    container = DockerContainer(RDF4J_IMAGE)
    container.with_exposed_ports(RDF4J_PORT)
    container.start()
    wait_for_logs(container, "oejs.Server:main: Started")
    yield container
    container.stop()


@pytest.fixture(scope="function")
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
    with RDF4JClient(f"http://localhost:{port}/", auth=("admin", "admin")) as client:
        yield client
