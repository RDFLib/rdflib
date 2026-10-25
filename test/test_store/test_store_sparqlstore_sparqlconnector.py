from __future__ import annotations

import json
import logging

import pytest

from rdflib.graph import Graph
from rdflib.plugins.stores.sparqlstore import SPARQLStore, SPARQLUpdateStore
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
    function_httpmock: ServedBaseHTTPServerMock, graph_identifier: str | None
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


@pytest.mark.parametrize("method", ["GET", "POST"])
@pytest.mark.parametrize("query_graph", [None, "http://example.com"])
def test_query_endpoint_with_query_string(
    function_httpmock: ServedBaseHTTPServerMock,
    method: str,
    query_graph: str | None,
) -> None:
    """
    Query string params in the endpoint URL are kept, and the params added for
    the request are joined to them with `&` instead of a second `?`.
    """
    store = SPARQLStore(
        f"{function_httpmock.url}/query?repository=default",
        returnFormat="json",
        method=method,
    )

    function_httpmock.responses[MethodName[method]].append(
        MockHTTPResponse(
            200,
            "OK",
            json.dumps({"head": {"vars": []}, "results": {"bindings": []}}).encode(
                encoding="utf-8"
            ),
            {"Content-Type": ["application/sparql-results+json"]},
        )
    )

    query = "SELECT ?s WHERE { ?s ?p ?o }"
    store.query(query, queryGraph=query_graph)

    request = function_httpmock.requests[MethodName[method]].pop()
    expected_query = {"repository": ["default"]}
    if query_graph is not None:
        expected_query["default-graph-uri"] = [query_graph]
    if method == "GET":
        expected_query["query"] = [query]
    assert request.parsed_path.path == "/query"
    assert request.path_query == expected_query


def test_update_endpoint_with_query_string(
    function_httpmock: ServedBaseHTTPServerMock,
) -> None:
    """
    Query string params in the update endpoint URL are kept as they are.
    """
    store = SPARQLUpdateStore(
        f"{function_httpmock.url}/query?repository=default",
        f"{function_httpmock.url}/update?repository=default",
    )

    function_httpmock.responses[MethodName.POST].append(
        MockHTTPResponse(
            200,
            "OK",
            b"Update succeeded",
            {"Content-Type": ["text/plain; charset=UTF-8"]},
        )
    )

    store.update("INSERT DATA { <urn:s> <urn:p> <urn:o> }")

    request = function_httpmock.requests[MethodName.POST].pop()
    assert request.parsed_path.path == "/update"
    assert request.path_query == {"repository": ["default"]}
