from __future__ import annotations

import json
import logging
from typing import Optional

import pytest

from rdflib.graph import Graph
from rdflib.plugins.stores.sparqlstore import SPARQLStore
from test.utils.http import MethodName, MockHTTPResponse
from test.utils.httpservermock import ServedBaseHTTPServerMock


@pytest.mark.parametrize(
    ["graph_identifier"],
    [
        (None,),
        ("http://example.com",),
    ],
)
def test_query_url_construct_format(
    function_httpmock: ServedBaseHTTPServerMock, graph_identifier: Optional[str]
) -> None:
    """
    This tests that query string params (foo & bar) are appended to the endpoint
    """
    endpoint = f"{function_httpmock.url}/query"

    store: SPARQLStore = SPARQLStore(
        sparql11=True,
        returnFormat="json",
        method="POST",
        params={"foo": "1", "bar": "2"},
    )
    graph: Graph = Graph(store=store, identifier=graph_identifier)
    graph.open(endpoint, create=True)

    query = """
    SELECT {
        ?s ?p ?o
    }
    WHERE {
        ?s ?p ?o
    }
    """

    function_httpmock.responses[MethodName.POST].append(
        MockHTTPResponse(
            200,
            "OK",
            json.dumps({"head": {"vars": []}, "results": {"bindings": []}}).encode(
                encoding="utf-8"
            ),
            {"Content-Type": ["application/sparql-results+json"]},
        )
    )

    result = graph.query(query)

    request = function_httpmock.requests[MethodName.POST].pop()
    logging.debug("request = %s", request)
    logging.debug("request.query_string = %s", request.path_query)
    assert "foo" in request.path_query
    assert request.path_query["foo"] == ["1"]
    assert "bar" in request.path_query
    assert request.path_query["bar"] == ["2"]
    if graph_identifier is None:
        assert "default-graph-uri" not in request.path_query
    else:
        assert "default-graph-uri" in request.path_query
        assert request.path_query["default-graph-uri"] == [graph_identifier]
    assert result.type == "SELECT"
