from __future__ import annotations

from unittest.mock import Mock

import pytest

from rdflib.contrib.rdf4j import has_httpx
from rdflib.contrib.rdf4j.exceptions import TransactionClosedError

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping rdf4j tests, httpx not available"
)

if has_httpx:
    import httpx

    from rdflib.contrib.rdf4j.client import (
        Repository,
        Transaction,
    )


def test_repo_transaction_size(txn: Transaction, monkeypatch: pytest.MonkeyPatch):
    mock_response = Mock(spec=httpx.Response, text="10")
    mock_httpx_put = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "put", mock_httpx_put)
    size = txn.size()
    mock_httpx_put.assert_called_once_with(
        txn.url,
        params={"action": "SIZE"},
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
