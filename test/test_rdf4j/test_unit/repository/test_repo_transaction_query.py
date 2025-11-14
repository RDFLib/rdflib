from __future__ import annotations

from unittest.mock import Mock

import pytest

from rdflib.contrib.rdf4j import has_httpx
from rdflib.graph import Graph
from rdflib.term import URIRef, Variable

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping rdf4j tests, httpx not available"
)

if has_httpx:
    import httpx

    from rdflib.contrib.rdf4j.client import (
        Transaction,
    )


@pytest.mark.parametrize(
    "query, accept_header, response_text, expected_result_type",
    [
        [
            "select ?s where { ?s ?p ?o }",
            "application/sparql-results+json",
            """
            {
                "head": {
                    "vars": ["s"]
                },
                "results": {
                    "bindings": [{"s": {"value": "http://example.com/s", "type": "uri"}}]
                }
            }
        """,
            "SELECT",
        ],
        [
            "ask where { ?s ?p ?o }",
            "application/sparql-results+json",
            '{ "boolean": true }',
            "ASK",
        ],
        [
            "construct { ?s ?p ?o } where { ?s ?p ?o }",
            "application/n-triples",
            "<http://example.com/s> <http://example.com/p> <http://example.com/o> .",
            "CONSTRUCT",
        ],
        [
            "describe ?s",
            "application/n-triples",
            "<http://example.com/s> <http://example.com/p> <http://example.com/o> .",
            "CONSTRUCT",
        ],
    ],
)
def test_repo_transaction_query(
    txn: Transaction,
    monkeypatch: pytest.MonkeyPatch,
    query: str,
    accept_header: str,
    response_text: str,
    expected_result_type,
):
    mock_response = Mock(
        spec=httpx.Response,
        content=response_text.encode("utf-8"),
        headers={"Content-Type": accept_header},
    )
    mock_httpx_put = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "put", mock_httpx_put)
    result = txn.query(query, infer="true")
    mock_httpx_put.assert_called_once_with(
        txn.url,
        params={"action": "QUERY", "query": query, "infer": "true"},
        headers={"Accept": accept_header},
    )

    if expected_result_type == "SELECT":
        assert len(result) == 1
        s_var = Variable("s")
        assert result.vars == [s_var]
        assert result.bindings[0].get(s_var) == URIRef("http://example.com/s")
    elif expected_result_type == "ASK":
        assert result.askAnswer is True
    elif expected_result_type == "CONSTRUCT":
        assert len(result.graph) == 1
        assert (
            Graph()
            .parse(
                data="<http://example.com/s> <http://example.com/p> <http://example.com/o> ."
            )
            .isomorphic(result.graph)
        )
    else:
        assert False, "Unexpected result type"
