from __future__ import annotations

from unittest.mock import Mock

import httpx
import pytest

from rdflib.contrib.rdf4j.client import (
    Transaction,
)


def test_repo_update(txn: Transaction, monkeypatch: pytest.MonkeyPatch):
    mock_response = Mock(spec=httpx.Response, status_code=204)
    mock_httpx_put = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "put", mock_httpx_put)
    query = "insert data { <http://example.org/s> <http://example.org/p> <http://example.org/o> }"
    txn.update(query)
    mock_httpx_put.assert_called_once_with(
        txn.url,
        params={"action": "UPDATE", "update": query},
    )
