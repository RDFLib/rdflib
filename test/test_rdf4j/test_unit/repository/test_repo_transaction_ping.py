from __future__ import annotations

from unittest.mock import Mock

import httpx
import pytest

from rdflib.contrib.rdf4j.client import (
    Transaction,
)
from rdflib.contrib.rdf4j.exceptions import (
    TransactionPingError,
)


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
