from __future__ import annotations

import typing as t
from unittest.mock import Mock

import pytest

from rdflib.contrib.rdf4j import has_httpx
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID
from rdflib.term import URIRef

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping rdf4j tests, httpx not available"
)

if has_httpx:
    import httpx

    from rdflib.contrib.rdf4j.client import (
        ObjectType,
        PredicateType,
        Repository,
        SubjectType,
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
    ],
)
def test_repo_delete_spo(
    repo: Repository,
    monkeypatch: pytest.MonkeyPatch,
    subj: SubjectType,
    pred: PredicateType,
    obj: ObjectType,
    expected_params: dict[str, str],
):
    """Test that the subj, pred, and obj query parameters are set correctly."""
    mock_response = Mock(spec=httpx.Response)
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "delete", mock_httpx_get)

    repo.delete(subj=subj, pred=pred, obj=obj)
    mock_httpx_get.assert_called_once_with(
        "/repositories/test-repo/statements",
        params=expected_params,
    )


@pytest.mark.parametrize(
    "graph_name, expected_graph_name_param",
    [
        [DATASET_DEFAULT_GRAPH_ID, "null"],
        ["http://example.com/graph", "<http://example.com/graph>"],
        [URIRef("http://example.com/graph"), "<http://example.com/graph>"],
        [None, None],
    ],
)
def test_repo_delete_graph_name(
    repo: Repository,
    graph_name: URIRef | t.Iterable[URIRef] | str | None,
    expected_graph_name_param: str,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Test that graph_name is passed as a query parameter and correctly handles the
    different type variations.
    """
    mock_response = Mock(spec=httpx.Response, text="")
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "delete", mock_httpx_get)
    if graph_name is None:
        params = {}
    else:
        params = {"context": expected_graph_name_param}
    repo.delete(graph_name=graph_name)
    mock_httpx_get.assert_called_once_with(
        "/repositories/test-repo/statements",
        params=params,
    )
