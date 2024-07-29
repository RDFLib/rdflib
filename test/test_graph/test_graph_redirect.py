from __future__ import annotations

from typing import Tuple
from urllib.parse import urlparse

from rdflib.graph import Graph
from test.data import SIMPLE_TRIPLE_GRAPH, TEST_DATA_DIR
from test.utils import GraphHelper
from test.utils.http import MethodName, MockHTTPResponse
from test.utils.httpservermock import ServedBaseHTTPServerMock


def test_graph_redirect_new_host(
    function_httpmocks: Tuple[ServedBaseHTTPServerMock, ServedBaseHTTPServerMock]
) -> None:
    """
    Redirect to new host results in a request with the right Host header
    parameter.
    """

    mock_a, mock_b = function_httpmocks

    mock_a.responses[MethodName.GET].append(
        MockHTTPResponse(
            308,
            "Permanent Redirect",
            b"",
            {"Location": [f"{mock_b.url}/b/data.ttl"]},
        )
    )

    mock_b.responses[MethodName.GET].append(
        MockHTTPResponse(
            200,
            "OK",
            (TEST_DATA_DIR / "variants" / "simple_triple.ttl").read_bytes(),
            {"Content-Type": ["text/turtle"]},
        )
    )

    graph = Graph()
    graph.parse(location=f"{mock_a.url}/a/data.ttl")
    GraphHelper.assert_sets_equals(graph, SIMPLE_TRIPLE_GRAPH)
    for mock in function_httpmocks:
        assert 1 == len(mock.requests[MethodName.GET])
        for request in mock.requests[MethodName.GET]:
            assert request.headers["Host"] == urlparse(mock.url).netloc
