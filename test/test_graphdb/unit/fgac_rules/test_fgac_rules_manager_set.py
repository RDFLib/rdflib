from __future__ import annotations

from unittest.mock import Mock

import pytest

from rdflib import Literal, URIRef
from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    import httpx

    from rdflib.contrib.graphdb.client import GraphDBClient, Repository
    from rdflib.contrib.graphdb.exceptions import (
        BadRequestError,
        ForbiddenError,
        InternalServerError,
        UnauthorisedError,
    )
    from rdflib.contrib.graphdb.models import (
        StatementAccessControlEntry,
        SystemAccessControlEntry,
    )


def test_fgac_set_sends_payload_and_handles_empty_response(
    client: GraphDBClient, monkeypatch: pytest.MonkeyPatch
):
    rule = StatementAccessControlEntry(
        scope="statement",
        policy="allow",
        role="user",
        operation="read",
        subject=URIRef("http://example.com/s"),
        predicate=URIRef("http://example.com/p"),
        object=Literal("o", lang="en"),
        graph=URIRef("http://example.com/g"),
    )
    mock_response = Mock(
        spec=httpx.Response,
        status_code=204,
        headers={"Content-Type": "application/json"},
    )
    mock_response.text = ""
    mock_response.raise_for_status = Mock()
    mock_httpx_put = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "put", mock_httpx_put)

    repo = Repository("repo", client.http_client)
    result = repo.acl.set([rule])

    assert result is None
    mock_response.raise_for_status.assert_called_once_with()
    mock_httpx_put.assert_called_once_with(
        "/rest/repositories/repo/acl",
        headers={"Content-Type": "application/json"},
        json=[
            {
                "scope": "statement",
                "policy": "allow",
                "role": "user",
                "operation": "read",
                "subject": "<http://example.com/s>",
                "predicate": "<http://example.com/p>",
                "object": '"o"@en',
                "context": "<http://example.com/g>",
            }
        ],
    )


def test_fgac_set_rejects_non_list_payload(client: GraphDBClient):
    repo = Repository("repo", client.http_client)
    with pytest.raises(
        ValueError, match="All ACL rules must be AccessControlEntry instances."
    ):
        repo.acl.set("not a list")  # type: ignore[arg-type]


def test_fgac_set_rejects_invalid_entries(
    client: GraphDBClient, monkeypatch: pytest.MonkeyPatch
):
    mock_httpx_put = Mock()
    monkeypatch.setattr(httpx.Client, "put", mock_httpx_put)

    repo = Repository("repo", client.http_client)
    with pytest.raises(
        ValueError, match="All ACL rules must be AccessControlEntry instances."
    ):
        repo.acl.set(["not an ACL entry"])  # type: ignore[list-item]
    mock_httpx_put.assert_not_called()


@pytest.mark.parametrize(
    "status_code, error_type",
    [
        (400, BadRequestError),
        (401, UnauthorisedError),
        (403, ForbiddenError),
        (500, InternalServerError),
    ],
)
def test_fgac_set_raises_http_errors(
    client: GraphDBClient,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
    error_type: type[Exception],
):
    rule = SystemAccessControlEntry(
        scope="system",
        policy="allow",
        role="admin",
        operation="read",
    )
    mock_response = Mock(spec=httpx.Response, status_code=status_code)
    mock_response.text = "Error"
    mock_error = httpx.HTTPStatusError(
        f"{status_code} Error", request=Mock(), response=mock_response
    )
    mock_response.raise_for_status = Mock(side_effect=mock_error)
    mock_httpx_put = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "put", mock_httpx_put)

    repo = Repository("repo", client.http_client)
    with pytest.raises(error_type):
        repo.acl.set([rule])
    mock_response.raise_for_status.assert_called_once_with()


def test_fgac_set_re_raises_other_http_errors(
    client: GraphDBClient, monkeypatch: pytest.MonkeyPatch
):
    rule = SystemAccessControlEntry(
        scope="system",
        policy="allow",
        role="admin",
        operation="read",
    )
    mock_response = Mock(spec=httpx.Response, status_code=404)
    mock_response.text = "Not Found"
    mock_error = httpx.HTTPStatusError(
        "404 Not Found", request=Mock(), response=mock_response
    )
    mock_response.raise_for_status = Mock(side_effect=mock_error)
    mock_httpx_put = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "put", mock_httpx_put)

    repo = Repository("repo", client.http_client)
    with pytest.raises(httpx.HTTPStatusError):
        repo.acl.set([rule])
    mock_response.raise_for_status.assert_called_once_with()
