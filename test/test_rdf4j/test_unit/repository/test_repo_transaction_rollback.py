from __future__ import annotations

from unittest.mock import Mock

import pytest

from rdflib.contrib.rdf4j import has_httpx
from rdflib.contrib.rdf4j.exceptions import TransactionClosedError, TransactionPingError

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping rdf4j tests, httpx not available"
)

if has_httpx:
    import httpx

    from rdflib.contrib.rdf4j.client import (
        Repository,
    )


def test_repo_transaction_rollback(
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
        mock_rollback_response = Mock(spec=httpx.Response, status_code=204)
        mock_httpx_delete = Mock(return_value=mock_rollback_response)
        monkeypatch.setattr(httpx.Client, "delete", mock_httpx_delete)
        txn.rollback()
        assert txn.url is None
        mock_httpx_delete.assert_called_once_with(
            transaction_url,
        )
        with pytest.raises(TransactionClosedError):
            txn.ping()

    mock_rollback_response = Mock(spec=httpx.Response, status_code=204)
    mock_httpx_delete = Mock(return_value=mock_rollback_response)
    monkeypatch.setattr(httpx.Client, "delete", mock_httpx_delete)
    with pytest.raises(TransactionPingError):
        with repo.transaction() as txn:
            mock_response = Mock(spec=httpx.Response, status_code=405)
            mock_httpx_put = Mock(return_value=mock_response)
            monkeypatch.setattr(httpx.Client, "put", mock_httpx_put)
            txn.ping()

    # Confirm transaction rollback is performed automatically.
    mock_httpx_delete.assert_called_once_with(
        transaction_url,
    )
