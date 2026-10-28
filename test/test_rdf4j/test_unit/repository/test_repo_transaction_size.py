from __future__ import annotations

from collections.abc import Iterable
from unittest.mock import Mock

import pytest

from rdflib.contrib.rdf4j import has_httpx
from rdflib.contrib.rdf4j.exceptions import TransactionClosedError
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID
from rdflib.term import BNode, IdentifiedNode, URIRef

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping rdf4j tests, httpx not available"
)

if has_httpx:
    import httpx2 as httpx

    from rdflib.contrib.rdf4j.client import (
        Repository,
        Transaction,
    )


@pytest.mark.parametrize(
    "graph_name, expected_context",
    [
        [None, None],
        [DATASET_DEFAULT_GRAPH_ID, "null"],
        [URIRef("urn:named"), "<urn:named>"],
        [BNode("blank"), "_:blank"],
        [[URIRef("urn:named"), BNode("blank")], ["<urn:named>", "_:blank"]],
    ],
)
def test_repo_transaction_size(
    txn: Transaction,
    monkeypatch: pytest.MonkeyPatch,
    graph_name: IdentifiedNode | Iterable[IdentifiedNode] | str | None,
    expected_context: str | list[str] | None,
):
    mock_response = Mock(spec=httpx.Response, text="10")
    mock_httpx_put = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "put", mock_httpx_put)
    size = txn.size(graph_name)
    params: dict[str, str | list[str]] = {"action": "SIZE"}
    if expected_context is not None:
        params["context"] = expected_context
    mock_httpx_put.assert_called_once_with(
        txn.url,
        params=params,
    )
    assert size == 10


def test_repo_transaction_size_closed(
    repo: Repository,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that size() raises TransactionClosedError on a closed transaction."""
    transaction_url = "http://example.com/transaction/1"
    mock_transaction_create_response = Mock(
        spec=httpx.Response, headers={"Location": transaction_url}
    )
    mock_httpx_post = Mock(return_value=mock_transaction_create_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)

    mock_commit_response = Mock(spec=httpx.Response, status_code=200)
    mock_httpx_put = Mock(return_value=mock_commit_response)
    monkeypatch.setattr(httpx.Client, "put", mock_httpx_put)

    with repo.transaction() as txn:
        txn.commit()
        with pytest.raises(TransactionClosedError):
            txn.size()
