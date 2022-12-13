from __future__ import annotations

import itertools
import json
import logging
from test.utils import GraphHelper
from test.utils.httpservermock import (
    MethodName,
    MockHTTPResponse,
    ServedBaseHTTPServerMock,
)
from typing import Dict, Iterable, List, Optional, Set, Tuple

import pytest
from _pytest.mark.structures import ParameterSet

from rdflib.graph import Graph
from rdflib.plugins.stores.sparqlstore import SPARQLStore


def test_query_url_construct_format(
    function_httpmock: ServedBaseHTTPServerMock,
) -> None:
    """
    This tests that query string params (foo & bar) are appended to the endpoint
    """
    endpoint = f"{function_httpmock.url}/query"

    store: SPARQLStore = SPARQLStore(
        sparql11=True,
        returnFormat="json",
        **{"method": "POST", "params": {"foo": "1", "bar": "2"}},
    )
    graph: Graph = Graph(store=store)
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
    assert "1" == request.path_query["foo"][0]
    assert "bar" in request.path_query
    assert "2" == request.path_query["bar"][0]
