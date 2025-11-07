from pathlib import Path

import pytest

from rdflib import Dataset, Graph, URIRef
from rdflib.contrib.rdf4j import has_httpx
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping rdf4j tests, httpx not available"
)

if has_httpx:
    from rdflib.contrib.rdf4j.client import Repository


@pytest.mark.parametrize(
    "graph_name", [URIRef("urn:graph:a"), DATASET_DEFAULT_GRAPH_ID]
)
@pytest.mark.testcontainer
def test_e2e_repo_graph_store_crud(repo: Repository, graph_name: URIRef):
    path = str(Path(__file__).parent.parent / "data/quads-2.nq")
    repo.overwrite(path, graph_name)
    assert repo.size() == 1

    graph = repo.graphs.get(graph_name)
    assert isinstance(graph, Graph)
    assert len(graph) == 1
    ds = Dataset().parse(path, format="nquads")
    expected_graph = Graph().parse(data=ds.serialize(format="ntriples"))
    assert len(expected_graph) == 1
    assert graph.isomorphic(expected_graph)

    # Add to the graph
    repo.graphs.add(
        graph_name,
        "<http://example.org/s4> <http://example.org/p4> <http://example.org/o4> .",
    )
    assert repo.size() == 2
    graph = repo.graphs.get(graph_name)
    assert isinstance(graph, Graph)
    assert len(graph) == 2
    expected_graph.add(
        (
            URIRef("http://example.org/s4"),
            URIRef("http://example.org/p4"),
            URIRef("http://example.org/o4"),
        )
    )
    assert graph.isomorphic(expected_graph)

    # Overwrite the graph
    repo.graphs.overwrite(
        graph_name,
        "<http://example.org/s5> <http://example.org/p5> <http://example.org/o5> .",
    )
    assert repo.size() == 1
    graph = repo.graphs.get(graph_name)
    assert isinstance(graph, Graph)
    assert len(graph) == 1
    expected_graph = Graph().parse(
        data="<http://example.org/s5> <http://example.org/p5> <http://example.org/o5> ."
    )
    assert graph.isomorphic(expected_graph)

    # Clear the graph
    repo.graphs.clear(graph_name)
    assert repo.size() == 0
    graph = repo.graphs.get(graph_name)
    assert isinstance(graph, Graph)
    assert len(graph) == 0
