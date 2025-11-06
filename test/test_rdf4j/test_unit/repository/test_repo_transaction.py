from __future__ import annotations

from unittest.mock import Mock

import httpx
import pytest

from rdflib.contrib.rdf4j.client import (
    Repository, Transaction,
)
from rdflib.contrib.rdf4j.exceptions import (
    TransactionClosedError,
    TransactionPingError,
)


@pytest.fixture
def txn(repo: Repository, monkeypatch: pytest.MonkeyPatch):
    transaction_url = "http://example.com/transaction/1"
    mock_transaction_create_response = Mock(
        spec=httpx.Response, headers={"Location": transaction_url}
    )
    mock_httpx_post = Mock(return_value=mock_transaction_create_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)
    with repo.transaction() as txn:
        yield txn
        mock_commit_response = Mock(spec=httpx.Response, status_code=200)
        mock_httpx_put = Mock(return_value=mock_commit_response)
        monkeypatch.setattr(httpx.Client, "put", mock_httpx_put)


def test_repo_transaction_commit(
    repo: Repository,
    monkeypatch: pytest.MonkeyPatch,
):
    transaction_url = "http://example.com/transaction/1"
    mock_transaction_create_response = Mock(
        spec=httpx.Response, headers={"Location": transaction_url}
    )
    mock_httpx_post = Mock(return_value=mock_transaction_create_response)
    monkeypatch.setattr(httpx.Client, "post", mock_httpx_post)
    with repo.transaction() as txn:
        # Ensure the transaction is created.
        assert txn.url == transaction_url
        mock_httpx_post.assert_called_once_with(
            "/repositories/test-repo/transactions",
        )

        # Mock commit response.
        mock_transaction_commit_response = Mock(spec=httpx.Response, status_code=200)
        mock_httpx_put = Mock(return_value=mock_transaction_commit_response)
        monkeypatch.setattr(httpx.Client, "put", mock_httpx_put)
        # Explicitly commit. This closes the transaction.
        txn.commit()
        mock_httpx_put.assert_called_once_with(
            transaction_url,
            params={"action": "COMMIT"},
        )
        # Ensure it is closed.
        assert txn.url is None
        with pytest.raises(TransactionClosedError):
            txn.ping()

    with repo.transaction() as txn:
        txn.ping()

    with pytest.raises(TransactionClosedError):
        # Ensure that the context manager closes the transaction.
        txn.ping()


def test_repo_transaction_ping(txn: Transaction, monkeypatch: pytest.MonkeyPatch):
    # Test a successful ping.
    mock_ping_response = Mock(spec=httpx.Response, status_code=200)
    mock_httpx_put = Mock(return_value=mock_ping_response)
    monkeypatch.setattr(httpx.Client, "put", mock_httpx_put)
    txn.ping()
    mock_httpx_put.assert_called_once_with(
        txn.url,
        params={"action": "PING"},
    )

    # Ensure it raises TransactionPingError.
    mock_ping_response = Mock(spec=httpx.Response, status_code=405)
    mock_httpx_put = Mock(return_value=mock_ping_response)
    monkeypatch.setattr(httpx.Client, "put", mock_httpx_put)
    with pytest.raises(TransactionPingError):
        txn.ping()


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
