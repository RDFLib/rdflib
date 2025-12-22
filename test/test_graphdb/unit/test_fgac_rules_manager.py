from __future__ import annotations

from unittest.mock import Mock

import pytest

from rdflib import Graph, Literal, URIRef
from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    import httpx

    from rdflib.contrib.graphdb.client import GraphDBClient, Repository
    from rdflib.contrib.graphdb.exceptions import ResponseFormatError
    from rdflib.contrib.graphdb.models import (
        ClearGraphAccessControlEntry,
        PluginAccessControlEntry,
        StatementAccessControlEntry,
        SystemAccessControlEntry,
    )


def test_fgac_list_builds_params_and_parses_entries(
    client: GraphDBClient, monkeypatch: pytest.MonkeyPatch
):
    acl_payload = [
        {
            "scope": "statement",
            "policy": "allow",
            "role": "user",
            "operation": "read",
            "subject": "<http://example.com/s>",
            "predicate": "<http://example.com/p>",
            "object": '"o"@en',
            "graph": "<http://example.com/g>",
        }
    ]
    mock_response = Mock(
        spec=httpx.Response,
        status_code=200,
        headers={"Content-Type": "application/json"},
    )
    mock_response.json = Mock(return_value=acl_payload)
    mock_response.raise_for_status = Mock()
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    repo = Repository("repo", client.http_client)
    result = repo.acl_rules.list()
    mock_httpx_get.assert_called_once_with("/rest/repositories/repo/acl", params={})

    assert len(result) == 1
    entry = result[0]
    assert isinstance(entry, StatementAccessControlEntry)
    assert entry.subject == URIRef("http://example.com/s")
    assert entry.object == Literal("o", lang="en")
    assert entry.graph == URIRef("http://example.com/g")


def test_fgac_list_parses_statement_wildcards(
    client: GraphDBClient, monkeypatch: pytest.MonkeyPatch
):
    acl_payload = [
        {
            "scope": "statement",
            "policy": "deny",
            "role": "guest",
            "operation": "*",
            "subject": "*",
            "predicate": "*",
            "object": "*",
            "graph": "named",
        }
    ]
    mock_response = Mock(
        spec=httpx.Response,
        status_code=200,
        headers={"Content-Type": "application/json"},
    )
    mock_response.json = Mock(return_value=acl_payload)
    mock_response.raise_for_status = Mock()
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    repo = Repository("repo", client.http_client)
    result = repo.acl_rules.list()

    assert len(result) == 1
    entry = result[0]
    assert isinstance(entry, StatementAccessControlEntry)
    assert entry.subject == "*"
    assert entry.predicate == "*"
    assert entry.object == "*"
    assert entry.graph == "named"
    assert entry.operation == "*"
    assert entry.policy == "deny"
    assert entry.role == "guest"


def test_fgac_list_rejects_non_list_payload(
    client: GraphDBClient, monkeypatch: pytest.MonkeyPatch
):
    mock_response = Mock(
        spec=httpx.Response,
        status_code=200,
        headers={"Content-Type": "application/json"},
    )
    mock_response.json = Mock(return_value={"scope": "statement"})
    mock_response.raise_for_status = Mock()
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    repo = Repository("repo", client.http_client)
    with pytest.raises(ResponseFormatError):
        repo.acl_rules.list()
    mock_httpx_get.assert_called_once_with("/rest/repositories/repo/acl", params={})


def test_fgac_list_formats_params(
    client: GraphDBClient, monkeypatch: pytest.MonkeyPatch
):
    mock_response = Mock(
        spec=httpx.Response,
        status_code=200,
        headers={"Content-Type": "application/json"},
    )
    mock_response.json = Mock(return_value=[])
    mock_response.raise_for_status = Mock()
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    repo = Repository("repo", client.http_client)
    repo.acl_rules.list(
        scope="statement",
        operation="write",
        subject=URIRef("http://example.com/s"),
        predicate=URIRef("http://example.com/p"),
        obj=Literal("o", lang="en"),
        graph=Graph(identifier=URIRef("http://example.com/g")),
        plugin="plugin",
        role="role",
        policy="deny",
    )

    mock_httpx_get.assert_called_once_with(
        "/rest/repositories/repo/acl",
        params={
            "scope": "statement",
            "operation": "write",
            "subject": "<http://example.com/s>",
            "predicate": "<http://example.com/p>",
            "object": '"o"@en',
            "graph": "<http://example.com/g>",
            "plugin": "plugin",
            "role": "role",
            "policy": "deny",
        },
    )


@pytest.mark.parametrize(
    "kwargs, error_match",
    [
        ({"scope": "unsupported"}, "Invalid FGAC scope filter"),
        ({"operation": "delete"}, "Invalid FGAC operation"),
        ({"policy": "invalid"}, "Invalid FGAC policy"),
        ({"role": 123}, "Invalid FGAC role"),
        ({"plugin": 123}, "Invalid FGAC plugin"),
        ({"subject": 123}, "Invalid FGAC subject filter"),
        ({"predicate": 123}, "Invalid FGAC predicate filter"),
        ({"obj": 123}, "Invalid FGAC object filter"),
        ({"graph": 123}, "Invalid FGAC graph filter"),
    ],
)
def test_fgac_list_rejects_invalid_filters(
    client: GraphDBClient, monkeypatch: pytest.MonkeyPatch, kwargs: dict, error_match: str
):
    mock_httpx_get = Mock()
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    repo = Repository("repo", client.http_client)
    with pytest.raises(ValueError, match=error_match):
        repo.acl_rules.list(**kwargs)
    mock_httpx_get.assert_not_called()


def test_fgac_list_parses_system_entry(
    client: GraphDBClient, monkeypatch: pytest.MonkeyPatch
):
    acl_payload = [
        {
            "scope": "system",
            "policy": "allow",
            "role": "admin",
            "operation": "read",
        }
    ]
    mock_response = Mock(
        spec=httpx.Response,
        status_code=200,
        headers={"Content-Type": "application/json"},
    )
    mock_response.json = Mock(return_value=acl_payload)
    mock_response.raise_for_status = Mock()
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    repo = Repository("repo", client.http_client)
    result = repo.acl_rules.list()

    assert len(result) == 1
    entry = result[0]
    assert isinstance(entry, SystemAccessControlEntry)
    assert entry.operation == "read"
    assert entry.policy == "allow"
    assert entry.role == "admin"


def test_fgac_list_parses_plugin_entry(
    client: GraphDBClient, monkeypatch: pytest.MonkeyPatch
):
    acl_payload = [
        {
            "scope": "plugin",
            "policy": "deny",
            "role": "user",
            "operation": "*",
            "plugin": "search",
        }
    ]
    mock_response = Mock(
        spec=httpx.Response,
        status_code=200,
        headers={"Content-Type": "application/json"},
    )
    mock_response.json = Mock(return_value=acl_payload)
    mock_response.raise_for_status = Mock()
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    repo = Repository("repo", client.http_client)
    result = repo.acl_rules.list()

    assert len(result) == 1
    entry = result[0]
    assert isinstance(entry, PluginAccessControlEntry)
    assert entry.plugin == "search"
    assert entry.operation == "*"
    assert entry.policy == "deny"


def test_fgac_list_parses_clear_graph_entry(
    client: GraphDBClient, monkeypatch: pytest.MonkeyPatch
):
    graph_uri = URIRef("http://example.com/g")
    acl_payload = [
        {
            "scope": "clear_graph",
            "policy": "abstain",
            "role": "maintainer",
            "graph": graph_uri.n3(),
        }
    ]
    mock_response = Mock(
        spec=httpx.Response,
        status_code=200,
        headers={"Content-Type": "application/json"},
    )
    mock_response.json = Mock(return_value=acl_payload)
    mock_response.raise_for_status = Mock()
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    repo = Repository("repo", client.http_client)
    result = repo.acl_rules.list()

    assert len(result) == 1
    entry = result[0]
    assert isinstance(entry, ClearGraphAccessControlEntry)
    assert entry.graph == graph_uri
    assert entry.policy == "abstain"
    assert entry.role == "maintainer"


@pytest.mark.parametrize(
    "payload, error_match",
    [
        ([{"scope": "system", "policy": "allow", "role": "admin"}], "Invalid FGAC operation"),
        (
            [
                {
                    "scope": "statement",
                    "policy": "allow",
                    "role": "user",
                    "operation": "read",
                    "predicate": "*",
                    "object": "*",
                    "graph": "*",
                }
            ],
            "Invalid FGAC subject",
        ),
        (
            [
                {
                    "scope": "plugin",
                    "policy": "allow",
                    "role": "user",
                    "operation": "read",
                }
            ],
            "Invalid FGAC plugin",
        ),
        (
            [
                {
                    "scope": "clear_graph",
                    "policy": "abstain",
                    "role": "maintainer",
                }
            ],
            "Invalid FGAC graph",
        ),
        (["not a mapping"], "ACL entry must be a mapping"),
    ],
)
def test_fgac_list_rejects_entries_with_missing_fields(
    client: GraphDBClient, monkeypatch: pytest.MonkeyPatch, payload: list, error_match: str
):
    mock_response = Mock(
        spec=httpx.Response,
        status_code=200,
        headers={"Content-Type": "application/json"},
    )
    mock_response.json = Mock(return_value=payload)
    mock_response.raise_for_status = Mock()
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    repo = Repository("repo", client.http_client)
    with pytest.raises(ResponseFormatError, match=error_match):
        repo.acl_rules.list()


def test_fgac_list_rejects_invalid_scope(
    client: GraphDBClient, monkeypatch: pytest.MonkeyPatch
):
    mock_response = Mock(
        spec=httpx.Response,
        status_code=200,
        headers={"Content-Type": "application/json"},
    )
    mock_response.json = Mock(return_value=[{"scope": "unknown"}])
    mock_response.raise_for_status = Mock()
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    repo = Repository("repo", client.http_client)
    with pytest.raises(ResponseFormatError):
        repo.acl_rules.list()
    mock_httpx_get.assert_called_once_with(
        "/rest/repositories/repo/acl",
        params={},
    )


def test_fgac_list_handles_empty_list(
    client: GraphDBClient, monkeypatch: pytest.MonkeyPatch
):
    mock_response = Mock(
        spec=httpx.Response,
        status_code=200,
        headers={"Content-Type": "application/json"},
    )
    mock_response.json = Mock(return_value=[])
    mock_response.raise_for_status = Mock()
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    repo = Repository("repo", client.http_client)
    result = repo.acl_rules.list()

    assert result == []
    mock_httpx_get.assert_called_once_with("/rest/repositories/repo/acl", params={})


def test_fgac_list_parses_mixed_entry_types(
    client: GraphDBClient, monkeypatch: pytest.MonkeyPatch
):
    acl_payload = [
        {
            "scope": "statement",
            "policy": "allow",
            "role": "user",
            "operation": "read",
            "subject": "*",
            "predicate": "*",
            "object": "*",
            "graph": "*",
        },
        {
            "scope": "system",
            "policy": "deny",
            "role": "admin",
            "operation": "write",
        },
        {
            "scope": "plugin",
            "policy": "allow",
            "role": "user",
            "operation": "*",
            "plugin": "search",
        },
        {
            "scope": "clear_graph",
            "policy": "abstain",
            "role": "guest",
            "graph": "default",
        },
    ]
    mock_response = Mock(
        spec=httpx.Response,
        status_code=200,
        headers={"Content-Type": "application/json"},
    )
    mock_response.json = Mock(return_value=acl_payload)
    mock_response.raise_for_status = Mock()
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    repo = Repository("repo", client.http_client)
    result = repo.acl_rules.list()

    assert len(result) == 4
    assert isinstance(result[0], StatementAccessControlEntry)
    assert isinstance(result[1], SystemAccessControlEntry)
    assert isinstance(result[2], PluginAccessControlEntry)
    assert isinstance(result[3], ClearGraphAccessControlEntry)


def test_fgac_list_raises_unauthorised_error_on_401(
    client: GraphDBClient, monkeypatch: pytest.MonkeyPatch
):
    mock_response = Mock(spec=httpx.Response, status_code=401)
    mock_response.text = "Unauthorized"
    mock_error = httpx.HTTPStatusError(
        "401 Unauthorized", request=Mock(), response=mock_response
    )
    mock_httpx_get = Mock(side_effect=mock_error)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    repo = Repository("repo", client.http_client)
    from rdflib.contrib.graphdb.exceptions import UnauthorisedError

    with pytest.raises(UnauthorisedError):
        repo.acl_rules.list()


def test_fgac_list_raises_forbidden_error_on_403(
    client: GraphDBClient, monkeypatch: pytest.MonkeyPatch
):
    mock_response = Mock(spec=httpx.Response, status_code=403)
    mock_response.text = "Forbidden"
    mock_error = httpx.HTTPStatusError(
        "403 Forbidden", request=Mock(), response=mock_response
    )
    mock_httpx_get = Mock(side_effect=mock_error)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    repo = Repository("repo", client.http_client)
    from rdflib.contrib.graphdb.exceptions import ForbiddenError

    with pytest.raises(ForbiddenError):
        repo.acl_rules.list()


def test_fgac_list_raises_internal_server_error_on_500(
    client: GraphDBClient, monkeypatch: pytest.MonkeyPatch
):
    mock_response = Mock(spec=httpx.Response, status_code=500)
    mock_response.text = "Internal Server Error"
    mock_error = httpx.HTTPStatusError(
        "500 Internal Server Error", request=Mock(), response=mock_response
    )
    mock_httpx_get = Mock(side_effect=mock_error)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    repo = Repository("repo", client.http_client)
    from rdflib.contrib.graphdb.exceptions import InternalServerError

    with pytest.raises(InternalServerError):
        repo.acl_rules.list()


def test_fgac_list_re_raises_other_http_errors(
    client: GraphDBClient, monkeypatch: pytest.MonkeyPatch
):
    mock_response = Mock(spec=httpx.Response, status_code=404)
    mock_response.text = "Not Found"
    mock_error = httpx.HTTPStatusError(
        "404 Not Found", request=Mock(), response=mock_response
    )
    mock_httpx_get = Mock(side_effect=mock_error)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    repo = Repository("repo", client.http_client)

    with pytest.raises(httpx.HTTPStatusError):
        repo.acl_rules.list()


def test_fgac_list_raises_format_error_on_invalid_json(
    client: GraphDBClient, monkeypatch: pytest.MonkeyPatch
):
    mock_response = Mock(
        spec=httpx.Response,
        status_code=200,
        headers={"Content-Type": "application/json"},
    )
    mock_response.json = Mock(side_effect=ValueError("Invalid JSON"))
    mock_response.raise_for_status = Mock()
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    repo = Repository("repo", client.http_client)

    with pytest.raises(ResponseFormatError):
        repo.acl_rules.list()


def test_fgac_list_parses_literal_object_with_datatype(
    client: GraphDBClient, monkeypatch: pytest.MonkeyPatch
):
    acl_payload = [
        {
            "scope": "statement",
            "policy": "allow",
            "role": "user",
            "operation": "read",
            "subject": "*",
            "predicate": "*",
            "object": '"42"^^<http://www.w3.org/2001/XMLSchema#integer>',
            "graph": "*",
        }
    ]
    mock_response = Mock(
        spec=httpx.Response,
        status_code=200,
        headers={"Content-Type": "application/json"},
    )
    mock_response.json = Mock(return_value=acl_payload)
    mock_response.raise_for_status = Mock()
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    repo = Repository("repo", client.http_client)
    result = repo.acl_rules.list()

    assert len(result) == 1
    entry = result[0]
    assert isinstance(entry, StatementAccessControlEntry)
    assert isinstance(entry.object, Literal)
    assert str(entry.object) == "42"


def test_fgac_list_parses_uriref_object(
    client: GraphDBClient, monkeypatch: pytest.MonkeyPatch
):
    acl_payload = [
        {
            "scope": "statement",
            "policy": "allow",
            "role": "user",
            "operation": "read",
            "subject": "*",
            "predicate": "*",
            "object": "<http://example.com/object>",
            "graph": "*",
        }
    ]
    mock_response = Mock(
        spec=httpx.Response,
        status_code=200,
        headers={"Content-Type": "application/json"},
    )
    mock_response.json = Mock(return_value=acl_payload)
    mock_response.raise_for_status = Mock()
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    repo = Repository("repo", client.http_client)
    result = repo.acl_rules.list()

    assert len(result) == 1
    entry = result[0]
    assert isinstance(entry, StatementAccessControlEntry)
    assert isinstance(entry.object, URIRef)
    assert entry.object == URIRef("http://example.com/object")


def test_fgac_list_parses_default_graph(
    client: GraphDBClient, monkeypatch: pytest.MonkeyPatch
):
    acl_payload = [
        {
            "scope": "statement",
            "policy": "allow",
            "role": "user",
            "operation": "read",
            "subject": "*",
            "predicate": "*",
            "object": "*",
            "graph": "default",
        }
    ]
    mock_response = Mock(
        spec=httpx.Response,
        status_code=200,
        headers={"Content-Type": "application/json"},
    )
    mock_response.json = Mock(return_value=acl_payload)
    mock_response.raise_for_status = Mock()
    mock_httpx_get = Mock(return_value=mock_response)
    monkeypatch.setattr(httpx.Client, "get", mock_httpx_get)

    repo = Repository("repo", client.http_client)
    result = repo.acl_rules.list()

    assert len(result) == 1
    entry = result[0]
    assert isinstance(entry, StatementAccessControlEntry)
    assert entry.graph == "default"
