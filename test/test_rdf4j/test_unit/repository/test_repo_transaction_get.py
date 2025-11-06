from __future__ import annotations

import typing as t
from unittest.mock import Mock

import httpx
import pytest

from rdflib import BNode, Dataset, Graph, IdentifiedNode, URIRef
from rdflib.contrib.rdf4j.client import (
    NamespaceManager,
    ObjectType,
    PredicateType,
    SubjectType,
    Transaction,
)
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID


def test_repo_transaction_get(txn: Transaction, monkeypatch: pytest.MonkeyPatch):
    mock_response = Mock(
        spec=httpx.Response,
        text="<http://example.org/s3> <http://example.org/p3> <http://example.org/o3> <urn:graph:a3> .",
    )
    mock_httpx_put = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "put", mock_httpx_put)
    monkeypatch.setattr(NamespaceManager, "list", lambda _: [])
    txn.get(pred=URIRef("http://example.org/p"))
    mock_httpx_put.assert_called_once_with(
        txn.url,
        headers={"Accept": "application/n-quads"},
        params={"action": "GET", "pred": "<http://example.org/p>"},
    )


@pytest.mark.parametrize(
    "content_type, data, expected_class_type",
    [
        [
            None,
            "<http://example.com/a> <http://example.com/b> <http://example.com/c> <http://example.com/d> .",
            Dataset,
        ],
        [
            "application/trig",
            "<http://example.com/d> { <http://example.com/a> <http://example.com/b> <http://example.com/c> . }",
            Dataset,
        ],
        [
            "application/n-triples",
            "<http://example.com/a> <http://example.com/b> <http://example.com/c> .",
            Graph,
        ],
        [
            "text/turtle",
            "<http://example.com/a> <http://example.com/b> <http://example.com/c> .",
            Graph,
        ],
        [
            "application/rdf+xml",
            """<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF
   xmlns:ns1="http://example.com/"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
>
  <rdf:Description rdf:about="http://example.com/a">
    <ns1:b rdf:resource="http://example.com/c"/>
  </rdf:Description>
</rdf:RDF>
""",
            Graph,
        ],
    ],
)
def test_repo_transaction_get_content_type(
    txn: Transaction,
    monkeypatch: pytest.MonkeyPatch,
    content_type: str | None,
    data: str,
    expected_class_type: type,
):
    """
    Test that the content type is set correctly on the request and that the response is
    parsed correctly.
    """
    mock_response = Mock(spec=httpx.Response, text=data)
    mock_httpx_put = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "put", mock_httpx_put)
    monkeypatch.setattr(NamespaceManager, "list", lambda _: [])

    result = txn.get(content_type=content_type)
    headers = {"Accept": content_type or "application/n-quads"}
    params: dict[str, str] = {"action": "GET"}
    mock_httpx_put.assert_called_once_with(
        txn.url,
        headers=headers,
        params=params,
    )
    assert isinstance(result, expected_class_type)


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
def test_repo_transaction_get_graph_name(
    txn: Transaction,
    monkeypatch: pytest.MonkeyPatch,
    graph_name: IdentifiedNode | t.Iterable[IdentifiedNode] | str | None,
    expected_graph_name_param: str,
):
    """
    Test that graph_name is passed as a query parameter and correctly handles the
    different type variations.
    """
    mock_response = Mock(spec=httpx.Response, text="")
    mock_httpx_put = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "put", mock_httpx_put)
    monkeypatch.setattr(NamespaceManager, "list", lambda _: [])
    headers = {
        "Accept": "application/n-quads",
    }
    if graph_name is None:
        params = {}
    else:
        params = {"context": expected_graph_name_param}
    params["action"] = "GET"
    txn.get(graph_name=graph_name)
    mock_httpx_put.assert_called_once_with(
        txn.url,
        headers=headers,
        params=params,
    )


@pytest.mark.parametrize("infer, expected_value", [[True, KeyError], [False, "false"]])
def test_repo_transaction_get_infer(
    txn: Transaction,
    monkeypatch: pytest.MonkeyPatch,
    infer: bool,
    expected_value: Exception | str,
):
    """Test that the "infer" query parameter is set correctly."""
    mock_response = Mock(spec=httpx.Response, text="")
    mock_httpx_put = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "put", mock_httpx_put)
    monkeypatch.setattr(NamespaceManager, "list", lambda _: [])
    headers = {
        "Accept": "application/n-quads",
    }

    params = {"action": "GET"}
    if isinstance(expected_value, str):
        params["infer"] = expected_value

    txn.get(infer=infer)
    mock_httpx_put.assert_called_once_with(
        txn.url,
        headers=headers,
        params=params,
    )


@pytest.mark.parametrize(
    "subj, pred, obj, expected_params",
    [
        [
            URIRef("http://example.com/s"),
            URIRef("http://example.com/p"),
            URIRef("http://example.com/o"),
            {
                "action": "GET",
                "subj": "<http://example.com/s>",
                "pred": "<http://example.com/p>",
                "obj": "<http://example.com/o>",
            },
        ],
        [
            None,
            None,
            None,
            {
                "action": "GET",
            },
        ],
        [
            BNode("some-bnode"),
            URIRef("http://example.com/p"),
            BNode("some-bnode-2"),
            {
                "action": "GET",
                "subj": "_:some-bnode",
                "pred": "<http://example.com/p>",
                "obj": "_:some-bnode-2",
            },
        ],
    ],
)
def test_repo_transaction_get_spo(
    txn: Transaction,
    monkeypatch: pytest.MonkeyPatch,
    subj: SubjectType,
    pred: PredicateType,
    obj: ObjectType,
    expected_params: dict[str, str],
):
    """Test that the subj, pred, and obj query parameters are set correctly."""
    mock_response = Mock(spec=httpx.Response, text="")
    mock_httpx_put = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "put", mock_httpx_put)
    monkeypatch.setattr(NamespaceManager, "list", lambda _: [])
    headers = {
        "Accept": "application/n-quads",
    }

    txn.get(subj=subj, pred=pred, obj=obj)
    mock_httpx_put.assert_called_once_with(
        txn.url,
        headers=headers,
        params=expected_params,
    )
