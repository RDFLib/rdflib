from __future__ import annotations

import itertools
import logging
from collections.abc import Iterable

import pytest
from _pytest.mark.structures import ParameterSet

from rdflib.graph import Graph
from rdflib.plugins.stores.sparqlstore import SPARQLStore
from test.utils import GraphHelper
from test.utils.http import MethodName, MockHTTPResponse
from test.utils.httpservermock import ServedBaseHTTPServerMock


def make_test_query_construct_format_cases() -> Iterable[ParameterSet]:
    """
    This only tests with application/rdf+xml as other result formats are not
    supported.
    """
    graphs: list[tuple[str, Graph]] = [
        (
            "basic",
            Graph().parse(
                format="turtle",
                data="""
        @prefix egdc: <http://example.com/> .

        egdc:s0 egdc:p0 egdc:o0;
            egdc:p1 egdc:o1;
            egdc:p2 "o2";
            egdc:p3 _:o3.


        egdc:s1 egdc:p4 egdc:o4;
            egdc:p5 egdc:o5;
            egdc:p6 "o6";
            egdc:p7 _:o7;
            egdc:p8 _:03.
        """,
            ),
        )
    ]
    response_format_encodings: list[tuple[str, str, set[str | None]]] = [
        (
            "application/rdf+xml",
            "utf-8",
            {
                "application/rdf+xml",
                "application/rdf+xml;charset=utf-8",
                "application/rdf+xml; charset=utf-8",
                "application/rdf+xml; charset=UTF-8",
            },
        ),
    ]
    for (mime_type, encoding, content_types), (
        graph_label,
        expected_graph,
    ) in itertools.product(response_format_encodings, graphs):
        response_body = expected_graph.serialize(format=mime_type, encoding=encoding)

        for content_type in content_types:
            if content_type is None:
                content_type = f"{mime_type};charset={encoding}"
            response_headers: dict[str, list[str]] = {"Content-Type": [content_type]}
            yield pytest.param(
                expected_graph,
                response_body,
                response_headers,
                id=f"{mime_type}-{encoding}-{graph_label}-ContentType_{content_type}",
            )


@pytest.mark.parametrize(
    [
        "expected_graph",
        "response_body",
        "response_headers",
    ],
    list(make_test_query_construct_format_cases()),
)
def test_query_construct_format(
    function_httpmock: ServedBaseHTTPServerMock,
    expected_graph: Graph,
    response_body: bytes,
    response_headers: dict[str, list[str]],
) -> None:
    """
    This tests that bindings for a variable named var
    """
    logging.debug("response_headers = %s", response_headers)
    graph = Graph(
        # store_factory(mime_type),
        "SPARQLStore",
        identifier="http://example.com",
        bind_namespaces="none",
    )
    url = f"{function_httpmock.url}/query"
    logging.debug("opening %s", url)
    graph.open(url)
    query = """
    CONSTRUCT {
        ?s ?p ?o
    }
    WHERE {
        ?s ?p ?o
    }
    """

    function_httpmock.responses[MethodName.GET].append(
        MockHTTPResponse(
            200,
            "OK",
            response_body,
            response_headers,
        )
    )

    logging.debug("sending query %s", query)
    result = graph.query(query)
    logging.debug("result = %s", result)
    assert result.type == "CONSTRUCT"
    assert result.graph is not None
    GraphHelper.assert_isomorphic(expected_graph, result.graph)

    request = function_httpmock.requests[MethodName.GET].pop()
    logging.debug("request = %s", request)
    logging.debug("request.headers = %s", request.headers.as_string())
    assert request.path_query["query"][0] == query


def test_query_jelly(function_httpmock: ServedBaseHTTPServerMock) -> None:
    """
    With returnFormat="jelly", the store asks for Jelly-SPARQL and Jelly-RDF,
    and reads the results of SELECT and CONSTRUCT queries in them.
    """
    expected_graph = Graph().parse(
        format="turtle",
        data="""
        @prefix egdc: <http://example.com/> .
        egdc:s0 egdc:p0 egdc:o0 , "o1" , _:o2 .
        """,
    )
    select_body = expected_graph.query("SELECT * { ?s ?p ?o }").serialize(
        format="jelly"
    )
    assert select_body is not None
    construct_body = expected_graph.serialize(format="jelly", encoding="utf-8")
    function_httpmock.responses[MethodName.GET].extend(
        [
            MockHTTPResponse(
                200,
                "OK",
                select_body,
                {"Content-Type": ["application/x-jelly-sparql"]},
            ),
            MockHTTPResponse(
                200,
                "OK",
                construct_body,
                {"Content-Type": ["application/x-jelly-rdf"]},
            ),
        ]
    )

    store = SPARQLStore(f"{function_httpmock.url}/query", returnFormat="jelly")
    graph = Graph(store, identifier="http://example.com")

    select_result = graph.query("SELECT * { ?s ?p ?o }")
    assert select_result.type == "SELECT"
    assert len(select_result) == 3
    request = function_httpmock.requests[MethodName.GET].pop()
    accept = {item.strip() for item in request.headers["Accept"].split(",")}
    assert accept == {"application/x-jelly-sparql", "application/x-jelly-rdf"}

    construct_result = graph.query("CONSTRUCT WHERE { ?s ?p ?o }")
    assert construct_result.type == "CONSTRUCT"
    assert construct_result.graph is not None
    GraphHelper.assert_isomorphic(expected_graph, construct_result.graph)
