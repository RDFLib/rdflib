from __future__ import annotations

import pytest

from rdflib import Literal, URIRef
from rdflib.contrib.rdf4j import has_httpx

pytestmark = pytest.mark.skipif(
    not has_httpx, reason="skipping graphdb tests, httpx not available"
)

if has_httpx:
    from rdflib.contrib.graphdb.models import (
        AccessControlEntry,
        ClearGraphAccessControlEntry,
        PluginAccessControlEntry,
        StatementAccessControlEntry,
        SystemAccessControlEntry,
        _parse_graph,
        _parse_object,
        _parse_operation,
        _parse_plugin,
        _parse_policy,
        _parse_predicate,
        _parse_role,
        _parse_subject,
    )


@pytest.mark.parametrize("policy", ["allow", "deny", "abstain"])
def test_parse_policy_valid(policy: str):
    result = _parse_policy(policy)
    assert result == policy


@pytest.mark.parametrize("invalid_policy", ["invalid", None, ""])
def test_parse_policy_invalid(invalid_policy: str | None):
    with pytest.raises(ValueError, match="Invalid FGAC policy"):
        _parse_policy(invalid_policy)


@pytest.mark.parametrize("operation", ["read", "write", "*"])
def test_parse_operation_valid(operation: str):
    result = _parse_operation(operation)
    assert result == operation


@pytest.mark.parametrize("invalid_operation", ["delete", None])
def test_parse_operation_invalid(invalid_operation: str | None):
    with pytest.raises(ValueError, match="Invalid FGAC operation"):
        _parse_operation(invalid_operation)


@pytest.mark.parametrize("role", ["admin", "user", ""])
def test_parse_role_valid(role: str):
    result = _parse_role(role)
    assert result == role


@pytest.mark.parametrize("invalid_role", [123, None])
def test_parse_role_invalid(invalid_role: int | None):
    with pytest.raises(ValueError, match="Invalid FGAC role"):
        _parse_role(invalid_role)


@pytest.mark.parametrize("plugin", ["elasticsearch-connector", "search", ""])
def test_parse_plugin_valid(plugin: str):
    result = _parse_plugin(plugin)
    assert result == plugin


@pytest.mark.parametrize("invalid_plugin", [123, None])
def test_parse_plugin_invalid(invalid_plugin: int | None):
    with pytest.raises(ValueError, match="Invalid FGAC plugin"):
        _parse_plugin(invalid_plugin)


def test_parse_subject_wildcard():
    result = _parse_subject("*")
    assert result == "*"


def test_parse_subject_uriref():
    uri = URIRef("http://example.com/subject")
    result = _parse_subject(uri)
    assert result == uri


def test_parse_subject_n3_string():
    result = _parse_subject("<http://example.com/subject>")
    assert isinstance(result, URIRef)
    assert result == URIRef("http://example.com/subject")


@pytest.mark.parametrize("invalid_subject", [123, '"some literal"'])
def test_parse_subject_invalid(invalid_subject: int | str):
    with pytest.raises(ValueError, match="Invalid FGAC subject"):
        _parse_subject(invalid_subject)


def test_parse_predicate_wildcard():
    result = _parse_predicate("*")
    assert result == "*"


def test_parse_predicate_uriref():
    uri = URIRef("http://example.com/predicate")
    result = _parse_predicate(uri)
    assert result == uri


def test_parse_predicate_n3_string():
    result = _parse_predicate("<http://example.com/predicate>")
    assert isinstance(result, URIRef)
    assert result == URIRef("http://example.com/predicate")


@pytest.mark.parametrize("invalid_predicate", [123, '"some literal"'])
def test_parse_predicate_invalid(invalid_predicate: int | str):
    with pytest.raises(ValueError, match="Invalid FGAC predicate"):
        _parse_predicate(invalid_predicate)


def test_parse_object_wildcard():
    result = _parse_object("*")
    assert result == "*"


def test_parse_object_uriref():
    uri = URIRef("http://example.com/object")
    result = _parse_object(uri)
    assert result == uri


def test_parse_object_literal():
    lit = Literal("test")
    result = _parse_object(lit)
    assert result == lit


def test_parse_object_n3_uriref():
    result = _parse_object("<http://example.com/object>")
    assert isinstance(result, URIRef)
    assert result == URIRef("http://example.com/object")


def test_parse_object_n3_literal():
    result = _parse_object('"test"')
    assert isinstance(result, Literal)
    assert str(result) == "test"


def test_parse_object_n3_literal_with_lang():
    result = _parse_object('"test"@en')
    assert isinstance(result, Literal)
    assert str(result) == "test"
    assert result.language == "en"


def test_parse_object_n3_literal_with_datatype():
    result = _parse_object('"42"^^<http://www.w3.org/2001/XMLSchema#integer>')
    assert isinstance(result, Literal)
    assert str(result) == "42"


def test_parse_object_invalid():
    with pytest.raises(ValueError, match="Invalid FGAC object"):
        _parse_object(123)


@pytest.mark.parametrize("graph_value", ["*", "named", "default"])
def test_parse_graph_wildcard_values(graph_value: str):
    result = _parse_graph(graph_value)
    assert result == graph_value


def test_parse_graph_uriref():
    uri = URIRef("http://example.com/graph")
    result = _parse_graph(uri)
    assert result == uri


def test_parse_graph_n3_string():
    result = _parse_graph("<http://example.com/graph>")
    assert isinstance(result, URIRef)
    assert result == URIRef("http://example.com/graph")


@pytest.mark.parametrize("invalid_graph", [123, '"some literal"'])
def test_parse_graph_invalid(invalid_graph: int | str):
    with pytest.raises(ValueError, match="Invalid FGAC graph"):
        _parse_graph(invalid_graph)


@pytest.mark.parametrize(
    "scope, expected_type, data",
    [
        (
            "statement",
            StatementAccessControlEntry,
            {
                "scope": "statement",
                "policy": "allow",
                "role": "user",
                "operation": "read",
                "subject": "<http://example.com/s>",
                "predicate": "<http://example.com/p>",
                "object": '"o"',
                "context": "<http://example.com/g>",
            },
        ),
        (
            "system",
            SystemAccessControlEntry,
            {
                "scope": "system",
                "policy": "deny",
                "role": "admin",
                "operation": "write",
            },
        ),
        (
            "plugin",
            PluginAccessControlEntry,
            {
                "scope": "plugin",
                "policy": "allow",
                "role": "user",
                "operation": "*",
                "plugin": "search",
            },
        ),
        (
            "clear_graph",
            ClearGraphAccessControlEntry,
            {
                "scope": "clear_graph",
                "policy": "abstain",
                "role": "maintainer",
                "context": "<http://example.com/g>",
            },
        ),
    ],
)
def test_from_dict_creates_entry_by_scope(scope: str, expected_type: type, data: dict):
    result = AccessControlEntry.from_dict(data)
    assert isinstance(result, expected_type)
    assert result.scope == scope


def test_from_dict_statement_entry_full_validation():
    data = {
        "scope": "statement",
        "policy": "allow",
        "role": "user",
        "operation": "read",
        "subject": "<http://example.com/s>",
        "predicate": "<http://example.com/p>",
        "object": '"o"',
        "context": "<http://example.com/g>",
    }
    result = AccessControlEntry.from_dict(data)
    assert isinstance(result, StatementAccessControlEntry)
    assert result.scope == "statement"
    assert result.policy == "allow"
    assert result.role == "user"
    assert result.operation == "read"
    assert result.subject == URIRef("http://example.com/s")
    assert result.predicate == URIRef("http://example.com/p")
    assert result.object == Literal("o")
    assert result.graph == URIRef("http://example.com/g")


def test_from_dict_statement_with_wildcards():
    data = {
        "scope": "statement",
        "policy": "allow",
        "role": "user",
        "operation": "*",
        "subject": "*",
        "predicate": "*",
        "object": "*",
        "context": "*",
    }
    result = AccessControlEntry.from_dict(data)
    assert isinstance(result, StatementAccessControlEntry)
    assert result.subject == "*"
    assert result.predicate == "*"
    assert result.object == "*"
    assert result.graph == "*"
    assert result.operation == "*"


@pytest.mark.parametrize("invalid_input", ["not a dict", [], None])
def test_from_dict_rejects_non_dict(invalid_input):
    with pytest.raises(TypeError, match="ACL entry must be a mapping"):
        AccessControlEntry.from_dict(invalid_input)


@pytest.mark.parametrize(
    "invalid_scope",
    [
        "unsupported",
        None,
    ],
)
def test_from_dict_rejects_invalid_scope(invalid_scope: str | None):
    data = {"scope": invalid_scope}
    with pytest.raises(ValueError, match="Unsupported FGAC scope"):
        AccessControlEntry.from_dict(data)


def test_from_dict_handles_missing_scope():
    data = {
        "policy": "allow",
        "role": "user",
        "operation": "read",
    }
    with pytest.raises(ValueError, match="Unsupported FGAC scope"):
        AccessControlEntry.from_dict(data)


@pytest.mark.parametrize(
    "field, invalid_value, error_match",
    [
        ("policy", "invalid", "Invalid FGAC policy"),
        ("operation", "delete", "Invalid FGAC operation"),
        ("role", 123, "Invalid FGAC role"),
    ],
)
def test_from_dict_rejects_invalid_system_fields(
    field: str, invalid_value, error_match: str
):
    data = {
        "scope": "system",
        "policy": "allow",
        "role": "admin",
        "operation": "read",
    }
    data[field] = invalid_value
    with pytest.raises(ValueError, match=error_match):
        AccessControlEntry.from_dict(data)


def test_from_dict_rejects_invalid_plugin():
    data = {
        "scope": "plugin",
        "policy": "allow",
        "role": "user",
        "operation": "read",
        "plugin": 123,
    }
    with pytest.raises(ValueError, match="Invalid FGAC plugin"):
        AccessControlEntry.from_dict(data)


@pytest.mark.parametrize(
    "data, error_match",
    [
        (
            {"scope": "system", "policy": "allow", "role": "admin"},
            "Invalid FGAC operation",
        ),
        (
            {
                "scope": "statement",
                "policy": "allow",
                "role": "user",
                "operation": "read",
                "predicate": "*",
                "object": "*",
                "context": "*",
            },
            "Invalid FGAC subject",
        ),
        (
            {
                "scope": "statement",
                "policy": "allow",
                "role": "user",
                "operation": "read",
                "subject": "*",
                "object": "*",
                "context": "*",
            },
            "Invalid FGAC predicate",
        ),
        (
            {
                "scope": "statement",
                "policy": "allow",
                "role": "user",
                "operation": "read",
                "subject": "*",
                "predicate": "*",
                "context": "*",
            },
            "Invalid FGAC object",
        ),
        (
            {
                "scope": "statement",
                "policy": "allow",
                "role": "user",
                "operation": "read",
                "subject": "*",
                "predicate": "*",
                "object": "*",
            },
            "Invalid FGAC graph",
        ),
        (
            {"scope": "plugin", "policy": "allow", "role": "user", "operation": "read"},
            "Invalid FGAC plugin",
        ),
        (
            {"scope": "clear_graph", "policy": "abstain", "role": "maintainer"},
            "Invalid FGAC graph",
        ),
    ],
)
def test_from_dict_rejects_missing_fields(data: dict, error_match: str):
    with pytest.raises(ValueError, match=error_match):
        AccessControlEntry.from_dict(data)


@pytest.mark.parametrize(
    "field, invalid_value, error_match",
    [
        ("subject", 123, "Invalid FGAC subject"),
        ("predicate", 123, "Invalid FGAC predicate"),
        ("object", 123, "Invalid FGAC object"),
        ("context", 123, "Invalid FGAC graph"),
    ],
)
def test_from_dict_rejects_invalid_statement_fields(
    field: str, invalid_value, error_match: str
):
    data = {
        "scope": "statement",
        "policy": "allow",
        "role": "user",
        "operation": "read",
        "subject": "*",
        "predicate": "*",
        "object": "*",
        "context": "*",
    }
    data[field] = invalid_value
    with pytest.raises(ValueError, match=error_match):
        AccessControlEntry.from_dict(data)
