from __future__ import annotations

from collections.abc import Callable, Generator
from importlib.util import find_spec
from pathlib import Path

import pytest

from rdflib import Dataset
from rdflib.contrib.rdf4j import has_httpx
from rdflib.store import Store

has_testcontainers = find_spec("testcontainers") is not None
pytestmark = [
    pytest.mark.testcontainer,
    pytest.mark.skipif(
        not (has_httpx and has_testcontainers),
        reason="httpx and testcontainers are required",
    ),
]

if has_httpx and has_testcontainers:
    import httpx
    from testcontainers.core.container import DockerContainer
    from testcontainers.core.waiting_utils import wait_for_logs

    from rdflib.contrib.rdf4j import RDF4JClient
    from rdflib.plugins.stores.rdf4j import RDF4JStore


@pytest.fixture(scope="module", params=["rdf4j", "graphdb"])
def quad_count_server(
    request: pytest.FixtureRequest,
) -> Generator[tuple[str, str], None, None]:
    if request.param == "rdf4j":
        image = "eclipse/rdf4j-workbench:5.2.2-jetty"
        port = 8080
        path = "/rdf4j-server/"
        ready_message = "Started ServerConnector"
        configuration = """
            @prefix config: <tag:rdf4j.org,2023:config/> .
            [] a config:Repository ;
               config:rep.id "quad-count" ;
               config:rep.impl [
                 config:rep.type "openrdf:SailRepository" ;
                 config:sail.impl [
                   config:sail.type "rdf4j:SchemaCachingRDFSInferencer" ;
                   config:delegate [ config:sail.type "openrdf:MemoryStore" ]
                 ]
               ] .
        """
    else:
        image = "ontotext/graphdb:10.8.12"
        port = 7200
        path = "/"
        ready_message = "Started GraphDB in workbench mode"
        configuration = (
            Path(__file__).parent / "repo-configs" / "test-graphdb-repo-config.ttl"
        ).read_text()
        configuration = configuration.replace('"test-repo"', '"quad-count"').replace(
            'graphdb:ruleset "empty"', 'graphdb:ruleset "rdfs-optimized"'
        )

    container = DockerContainer(image).with_exposed_ports(port)
    if request.param == "graphdb":
        container.with_env("GDB_JAVA_OPTS", "-Xmx1g")
    with container:
        wait_for_logs(container, ready_message)
        host = container.get_container_host_ip()
        host_port = container.get_exposed_port(port)
        yield f"http://{host}:{host_port}{path}", configuration


@pytest.mark.parametrize("measure", [len, bool], ids=["length", "truth"])
def test_native_quad_count(
    quad_count_server: tuple[str, str], measure: Callable[[Dataset], int]
) -> None:
    url, configuration = quad_count_server
    with RDF4JClient(url) as client:
        repo = client.repositories.create("quad-count", configuration)
        try:
            assert repo.size() == 0
            repo.upload(
                """
                <urn:s> <urn:p> <urn:o> .
                <urn:s> <urn:p> <urn:o> <urn:named> .
                <urn:s> <urn:p> <urn:o> _:blank .
                <urn:Child> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <urn:Parent> .
                <urn:s> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <urn:Child> .
                """,
                content_type="application/n-quads",
            )
            query = "ASK { <urn:s> a <urn:Parent> }"
            assert repo.query(query, infer="true").askAnswer is True
            assert repo.query(query, infer="false").askAnswer is False

            requests: list[httpx.Request] = []
            store = RDF4JStore(
                url, "quad-count", event_hooks={"request": [requests.append]}
            )
            try:
                dataset = Dataset(store)
                assert Store.quad_count(store) == 5
                assert len(dataset.default_graph) == 3
                requests.clear()

                assert measure(dataset) == (5 if measure is len else True)
                assert len(requests) == 1
                assert requests[0].method == "GET"
                assert requests[0].url.path.endswith("/repositories/quad-count/size")
                assert not requests[0].url.params
            finally:
                store.close()
        finally:
            client.repositories.delete("quad-count")
