from __future__ import annotations

from unittest.mock import ANY, Mock

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


@pytest.mark.parametrize(
    "base_uri, content_type, expected_headers, expected_params",
    [
        [None, None, {"Content-Type": "application/n-quads"}, {"action": "DELETE"}],
        [
            "http://example.com/",
            "text/turtle",
            {"Content-Type": "text/turtle"},
            {"action": "DELETE", "baseURI": "http://example.com/"},
        ],
    ],
)
def test_repo_transaction_delete(
    txn: Transaction,
    monkeypatch: pytest.MonkeyPatch,
    base_uri: str | None,
    content_type: str | None,
    expected_headers: dict[str, str],
    expected_params: dict[str, str],
):
    mock_response = Mock(spec=httpx.Response)
    mock_httpx_put = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "put", mock_httpx_put)
    txn.delete("", base_uri, content_type)

    mock_httpx_put.assert_called_once_with(
        txn.url,
        headers=expected_headers,
        params=expected_params,
        content=ANY,
    )


def test_repo_transaction_delete_closed(
    repo: Repository,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that delete() raises TransactionClosedError on a closed transaction."""
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
            txn.delete("")
