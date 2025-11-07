from __future__ import annotations

import typing as t
from unittest.mock import Mock

import pytest

from rdflib import Dataset, Graph
from rdflib.contrib.rdf4j import has_httpx
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID
from rdflib.term import BNode, IdentifiedNode, URIRef

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping rdf4j tests, httpx not available"
)

if has_httpx:
    import httpx
    from rdflib.contrib.rdf4j.client import (
        NamespaceManager,
        ObjectType,
        PredicateType,
        Repository,
        SubjectType,
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
def test_repo_content_type(
    repo: Repository,
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
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)
    monkeypatch.setattr(NamespaceManager, "list", lambda _: [])

    result = repo.get(content_type=content_type)
    headers = {"Accept": content_type or "application/n-quads"}
    params: dict[str, str] = {}
    mock_httpx_get.assert_called_once_with(
        "/repositories/test-repo/statements",
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
def test_repo_get_graph_name(
    repo: Repository,
    monkeypatch: pytest.MonkeyPatch,
    graph_name: IdentifiedNode | t.Iterable[IdentifiedNode] | str | None,
    expected_graph_name_param: str,
):
    """
    Test that graph_name is passed as a query parameter and correctly handles the
    different type variations.
    """
    mock_response = Mock(spec=httpx.Response, text="")
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)
    monkeypatch.setattr(NamespaceManager, "list", lambda _: [])
    headers = {
        "Accept": "application/n-quads",
    }
    if graph_name is None:
        params = {}
    else:
        params = {"context": expected_graph_name_param}
    repo.get(graph_name=graph_name)
    mock_httpx_get.assert_called_once_with(
        "/repositories/test-repo/statements",
        headers=headers,
        params=params,
    )


@pytest.mark.parametrize("infer, expected_value", [[True, KeyError], [False, "false"]])
def test_repo_get_infer(
    repo: Repository,
    monkeypatch: pytest.MonkeyPatch,
    infer: bool,
    expected_value: Exception | str,
):
    """Test that the "infer" query parameter is set correctly."""
    mock_response = Mock(spec=httpx.Response, text="")
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)
    monkeypatch.setattr(NamespaceManager, "list", lambda _: [])
    headers = {
        "Accept": "application/n-quads",
    }

    params = {}
    if isinstance(expected_value, str):
        params["infer"] = expected_value

    repo.get(infer=infer)
    mock_httpx_get.assert_called_once_with(
        "/repositories/test-repo/statements",
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
                "subj": "<http://example.com/s>",
                "pred": "<http://example.com/p>",
                "obj": "<http://example.com/o>",
            },
        ],
        [None, None, None, {}],
        [
            BNode("some-bnode"),
            URIRef("http://example.com/p"),
            BNode("some-bnode-2"),
            {
                "subj": "_:some-bnode",
                "pred": "<http://example.com/p>",
                "obj": "_:some-bnode-2",
            },
        ],
    ],
)
def test_repo_get_spo(
    repo: Repository,
    monkeypatch: pytest.MonkeyPatch,
    subj: SubjectType,
    pred: PredicateType,
    obj: ObjectType,
    expected_params: dict[str, str],
):
    """Test that the subj, pred, and obj query parameters are set correctly."""
    mock_response = Mock(spec=httpx.Response, text="")
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)
    monkeypatch.setattr(NamespaceManager, "list", lambda _: [])
    headers = {
        "Accept": "application/n-quads",
    }

    repo.get(subj=subj, pred=pred, obj=obj)
    mock_httpx_get.assert_called_once_with(
        "/repositories/test-repo/statements",
        headers=headers,
        params=expected_params,
    )
