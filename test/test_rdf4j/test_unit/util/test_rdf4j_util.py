import pytest

from rdflib.contrib.rdf4j.util import build_context_param
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID
from rdflib.term import BNode, URIRef


@pytest.mark.parametrize(
    "graph_name, expected_graph_name_param",
    [
        [DATASET_DEFAULT_GRAPH_ID, "null"],
        ["http://example.com/graph", "<http://example.com/graph>"],
        [URIRef("http://example.com/graph"), "<http://example.com/graph>"],
        [BNode("some-bnode"), "_:some-bnode"],
        [
            [URIRef("http://example.com/graph"), BNode("some-bnode")],
            "<http://example.com/graph>,_:some-bnode",
        ],
        [None, None],
    ],
)
def test_build_context_param(graph_name, expected_graph_name_param):
    params = {}
    build_context_param(params, graph_name)
    if graph_name is None:
        assert "context" not in params
    else:
        assert params["context"] == expected_graph_name_param
