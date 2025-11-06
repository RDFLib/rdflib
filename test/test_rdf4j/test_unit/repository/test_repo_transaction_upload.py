from unittest.mock import ANY, Mock

import httpx
import pytest

from rdflib.contrib.rdf4j.client import Transaction


def test_repo_transaction_upload(txn: Transaction, monkeypatch: pytest.MonkeyPatch):
    mock_response = Mock(spec=httpx.Response)
    mock_httpx_put = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "put", mock_httpx_put)
    txn.upload("")
    mock_httpx_put.assert_called_once_with(
        txn.url,
        headers={"Content-Type": "application/n-quads"},
        params={"action": "ADD"},
        content=ANY,
    )
