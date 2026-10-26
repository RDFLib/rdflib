from __future__ import annotations

import json
import logging
import time
from collections.abc import Iterator, Mapping, Sequence
from http.client import (
    HTTPMessage,
    HTTPResponse,
    IncompleteRead,
    RemoteDisconnected,
)
from io import BytesIO
from typing import Any, Optional, Union
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs
from urllib.request import BaseHandler, HTTPHandler, OpenerDirector, Request, urlopen
from urllib.response import addinfourl

import pytest

from rdflib import Graph, Literal, URIRef, Variable, __version__
from rdflib.namespace import XSD
from rdflib.plugins.sparql import evaluate, prepareQuery
from rdflib.plugins.sparql.algebra import traverse
from rdflib.plugins.sparql.parserutils import CompValue
from rdflib.plugins.sparql.sparql import FrozenBindings, QueryContext
from rdflib.term import BNode, Identifier
from test.utils import helper
from test.utils.audit import AuditHookDispatcher, AuditHookType
from test.utils.http import MethodName, MockHTTPResponse
from test.utils.httpservermock import ServedBaseHTTPServerMock
from test.utils.outcome import OutcomeChecker
from test.utils.urlopen import context_urlopener


@pytest.mark.webtest
def test_service():
    g = Graph()
    q = """
        SELECT ?p ?o
        WHERE {
            SERVICE <http://DBpedia.org/sparql> {
                SELECT ?p ?o
                WHERE {
                    <http://dbpedia.org/resource/John_Lilburne> ?p ?o
                }
            }
        }
        LIMIT 2
    """
    try:
        results = helper.query_with_retry(g, q)
    except (RemoteDisconnected, IncompleteRead):
        pytest.skip("this test uses dbpedia which is down sometimes")
    print(results.vars)
    print(results.bindings)
    assert len(results) == 2

    for r in results:
        assert len(r) == 2


@pytest.mark.webtest
def test_service_with_bind():
    g = Graph()
    q = """
        PREFIX dbp:	<http://dbpedia.org/property/>
        SELECT ?sameAs ?dbpComment ?subject
        WHERE {
        BIND(<http://dbpedia.org/resource/Category:1614_births> AS ?subject)
        SERVICE <http://DBpedia.org/sparql> {
            SELECT ?sameAs ?dbpComment ?subject
            WHERE {
                <http://dbpedia.org/resource/John_Lilburne>
                    <http://www.w3.org/2002/07/owl#sameAs> ?sameAs ;
                    dbp:caption ?dbpComment ;
                    <http://purl.org/dc/terms/subject> ?subject .
                }
            }
        }
        LIMIT 2
    """
    try:
        results = helper.query_with_retry(g, q)
    except (RemoteDisconnected, IncompleteRead):
        pytest.skip("this test uses dbpedia which is down sometimes")
    assert len(results) == 2

    for r in results:
        assert len(r) == 3


@pytest.mark.webtest
def test_service_with_bound_solutions():
    g = Graph()
    g.update(
        """
        INSERT DATA {
          []
            <http://www.w3.org/2002/07/owl#sameAs> <http://de.dbpedia.org/resource/John_Lilburne> ;
            <http://purl.org/dc/terms/subject> <http://dbpedia.org/resource/Category:1614_births> .
        }
        """
    )
    q = """
            PREFIX dbp:	<http://dbpedia.org/property/>
            SELECT ?sameAs ?dbpComment ?subject
            WHERE {
            []
                <http://www.w3.org/2002/07/owl#sameAs> ?sameAs ;
                <http://purl.org/dc/terms/subject> ?subject .

            SERVICE <http://DBpedia.org/sparql> {
                SELECT ?sameAs ?dbpComment ?subject
                WHERE {
                    <http://dbpedia.org/resource/John_Lilburne>
                        <http://www.w3.org/2002/07/owl#sameAs> ?sameAs ;
                        dbp:caption ?dbpComment ;
                        <http://purl.org/dc/terms/subject> ?subject .
                    }
                }
            }
            LIMIT 2
        """
    try:
        results = helper.query_with_retry(g, q)
    except (RemoteDisconnected, IncompleteRead):
        pytest.skip("this test uses dbpedia which is down sometimes")
    assert len(results) == 1

    for r in results:
        assert len(r) == 3


@pytest.mark.webtest
def test_service_with_values():
    g = Graph()
    q = """
        PREFIX dbp:	<http://dbpedia.org/property/>
        SELECT ?sameAs ?dbpComment ?subject
        WHERE {
            VALUES (?sameAs ?subject) {
                (<http://de.dbpedia.org/resource/John_Lilburne> <http://dbpedia.org/resource/Category:1614_births>) (<https://global.dbpedia.org/id/4t6Fk> <http://dbpedia.org/resource/Category:Levellers>)
            }
            SERVICE <http://DBpedia.org/sparql> {
                SELECT ?sameAs ?dbpComment ?subject
                WHERE {
                    <http://dbpedia.org/resource/John_Lilburne>
                        <http://www.w3.org/2002/07/owl#sameAs> ?sameAs ;
                        dbp:caption ?dbpComment ;
                        <http://purl.org/dc/terms/subject> ?subject .
                }
            }
        }
        LIMIT 2
    """
    try:
        results = helper.query_with_retry(g, q)
    except (RemoteDisconnected, IncompleteRead, URLError):
        pytest.skip("this test uses dbpedia which is sometimes unavailable")
    assert len(results) == 2

    for r in results:
        assert len(r) == 3


@pytest.mark.webtest
def test_service_with_implicit_select():
    g = Graph()
    q = """select ?s ?p ?o
    where
    {
      service <https://DBpedia.org/sparql>
    {
      values (?s ?p ?o) {(<http://example.org/a> <http://example.org/b> 1) (<http://example.org/a> <http://example.org/b> 2)}
    }} limit 2"""
    try:
        results = helper.query_with_retry(g, q)
    except (RemoteDisconnected, IncompleteRead):
        pytest.skip("this test uses dbpedia which is down sometimes")
    assert len(results) == 2

    for r in results:
        assert len(r) == 3


@pytest.mark.webtest
def test_service_with_implicit_select_and_prefix():
    g = Graph()
    q = """prefix ex:<http://example.org/>
    select ?s ?p ?o
    where
    {
      service <https://DBpedia.org/sparql>
    {
      values (?s ?p ?o) {(ex:a ex:b 1) (<http://example.org/a> <http://example.org/b> 2)}
    }} limit 2"""
    try:
        results = helper.query_with_retry(g, q)
    except (RemoteDisconnected, IncompleteRead):
        pytest.skip("this test uses dbpedia which is down sometimes")
    assert len(results) == 2

    for r in results:
        assert len(r) == 3


@pytest.mark.webtest
def test_service_with_implicit_select_and_base():
    g = Graph()
    q = """base <http://example.org/>
    select ?s ?p ?o
    where
    {
      service <https://DBpedia.org/sparql>
    {
      values (?s ?p ?o) {(<a> <b> 1) (<a> <b> 2)}
    }} limit 2"""
    try:
        results = helper.query_with_retry(g, q)
    except (RemoteDisconnected, IncompleteRead):
        pytest.skip("this test uses dbpedia which is down sometimes")
    assert len(results) == 2

    for r in results:
        assert len(r) == 3


@pytest.mark.webtest
def test_service_with_implicit_select_and_allcaps():
    g = Graph()
    q = """SELECT ?s
    WHERE
    {
      SERVICE <https://dbpedia.org/sparql>
      {
        ?s <http://www.w3.org/2002/07/owl#sameAs> ?sameAs .
      }
    } LIMIT 3"""
    try:
        results = helper.query_with_retry(g, q)
    except (RemoteDisconnected, IncompleteRead):
        pytest.skip("this test uses dbpedia which is down sometimes")
    assert len(results) == 3


def freeze_bindings(
    bindings: Sequence[Mapping[Variable, Identifier]],
) -> frozenset[frozenset[tuple[Variable, Identifier]]]:
    result = []
    for binding in bindings:
        result.append(frozenset(((key, value)) for key, value in binding.items()))
    return frozenset(result)


@pytest.mark.webtest
def test_simple_not_null():
    """Test service returns simple literals not as NULL.

    Issue: https://github.com/RDFLib/rdflib/issues/1278
    """

    g = Graph()
    q = """SELECT ?s ?p ?o
WHERE {
    SERVICE <https://DBpedia.org/sparql> {
        VALUES (?s ?p ?o) {(<http://example.org/a> <http://example.org/b> "c")}
    }
}"""
    try:
        results = helper.query_with_retry(g, q)
    except (RemoteDisconnected, IncompleteRead):
        pytest.skip("this test uses dbpedia which is down sometimes")
    assert results.bindings[0].get(Variable("o")) == Literal("c")


@pytest.mark.webtest
def test_service_node_types():
    """Test if SERVICE properly returns different types of nodes:
    - URI;
    - Simple Literal;
    - Literal with datatype ;
    - Literal with language tag .
    """

    g = Graph()
    q = """
SELECT ?o
WHERE {
    SERVICE <https://dbpedia.org/sparql> {
        VALUES (?s ?p ?o) {
            (<http://example.org/a> <http://example.org/uri> <http://example.org/URI>)
            (<http://example.org/a> <http://example.org/simpleLiteral> "Simple Literal")
            (<http://example.org/a> <http://example.org/dataType> "String Literal"^^xsd:string)
            (<http://example.org/a> <http://example.org/language> "String Language"@en)
            (<http://example.org/a> <http://example.org/language> "String Language"@en)
        }
    }
    FILTER( ?o IN (<http://example.org/URI>, "Simple Literal", "String Literal"^^xsd:string, "String Language"@en) )
}"""
    try:
        results = helper.query_with_retry(g, q)
    except (RemoteDisconnected, IncompleteRead):
        pytest.skip("this test uses dbpedia which is down sometimes")

    expected = freeze_bindings(
        [
            {Variable("o"): URIRef("http://example.org/URI")},
            {Variable("o"): Literal("Simple Literal")},
            {
                Variable("o"): Literal(
                    "String Literal",
                    datatype=URIRef("http://www.w3.org/2001/XMLSchema#string"),
                )
            },
            {Variable("o"): Literal("String Language", lang="en")},
        ]
    )
    assert expected == freeze_bindings(results.bindings)


@pytest.mark.parametrize(
    ("response_bindings", "expected_result"),
    [
        (
            [
                {"type": "uri", "value": "http://example.org/uri"},
                {"type": "literal", "value": "literal without type or lang"},
                {"type": "literal", "value": "literal with lang", "xml:lang": "en"},
                {
                    "type": "typed-literal",
                    "value": "typed-literal with datatype",
                    "datatype": f"{XSD.string}",
                },
                {
                    "type": "literal",
                    "value": "literal with datatype",
                    "datatype": f"{XSD.string}",
                },
                {"type": "bnode", "value": "ohci6Te6aidooNgo"},
            ],
            [
                URIRef("http://example.org/uri"),
                Literal("literal without type or lang"),
                Literal("literal with lang", lang="en"),
                Literal(
                    "typed-literal with datatype",
                    datatype=URIRef("http://www.w3.org/2001/XMLSchema#string"),
                ),
                Literal("literal with datatype", datatype=XSD.string),
                BNode("ohci6Te6aidooNgo"),
            ],
        ),
        (
            [
                {"type": "invalid-type"},
            ],
            ValueError,
        ),
    ],
)
def test_with_mock(
    function_httpmock: ServedBaseHTTPServerMock,
    response_bindings: list[dict[str, str]],
    expected_result: Union[list[Identifier], type[Exception]],
) -> None:
    """
    This tests that bindings for a variable named var
    """
    graph = Graph()
    query = """
    PREFIX ex: <http://example.org/>
    SELECT ?var
    WHERE {
        SERVICE <REMOTE_URL> {
            ex:s ex:p ?var
        }
    }
    """
    query = query.replace("REMOTE_URL", function_httpmock.url)
    response = {
        "head": {"vars": ["var"]},
        "results": {"bindings": [{"var": item} for item in response_bindings]},
    }
    mock_response = MockHTTPResponse(
        200,
        "OK",
        json.dumps(response).encode("utf-8"),
        {"Content-Type": ["application/sparql-results+json"]},
    )
    # Adding the same response for GET and POST as the method used by RDFLib is
    # dependent on the size of the service query.
    function_httpmock.responses[MethodName.GET].append(mock_response)
    function_httpmock.responses[MethodName.POST].append(mock_response)

    checker = OutcomeChecker[Sequence[Mapping[Variable, Identifier]]].from_primitive(
        [{Variable("var"): item} for item in expected_result]
        if isinstance(expected_result, list)
        else expected_result
    )
    with checker.context():
        bindings = graph.query(query).bindings
        checker.check(bindings)


@pytest.mark.parametrize(
    ("method", "value"),
    [(MethodName.GET, "short"), (MethodName.POST, "x" * 700)],
    ids=["GET", "POST"],
)
def test_service_user_agent(
    function_httpmock: ServedBaseHTTPServerMock, method: MethodName, value: str
) -> None:
    # Use an explicit SELECT so automatic prefix insertion does not make the
    # short query exceed the GET size limit. The long literal forces POST.
    query = f"""
    SELECT ?var WHERE {{
        SERVICE <{function_httpmock.url}> {{
            SELECT ?var WHERE {{ VALUES ?var {{ "{value}" }} }}
        }}
    }}
    """
    response = {
        "head": {"vars": ["var"]},
        "results": {"bindings": [{"var": {"type": "literal", "value": value}}]},
    }
    function_httpmock.responses[method].append(
        MockHTTPResponse(
            200,
            "OK",
            json.dumps(response).encode("utf-8"),
            {"Content-Type": ["application/sparql-results+json"]},
        )
    )

    assert Graph().query(query).bindings == [{Variable("var"): Literal(value)}]
    assert function_httpmock.call_count == 1
    assert len(function_httpmock.requests[method]) == 1
    request = function_httpmock.requests[method][0]
    assert request.method == method
    assert request.headers["User-Agent"] == f"rdflib/{__version__}"


def test_service_raw_tab_in_string_literal(
    function_httpmock: ServedBaseHTTPServerMock,
) -> None:
    # The raw TAB must reach the endpoint unchanged, see
    # https://github.com/RDFLib/rdflib/issues/3586
    query = f"""
    SELECT ?var WHERE {{
        SERVICE <{function_httpmock.url}> {{
            SELECT ?var WHERE {{ VALUES ?var {{ "a\tb" }} }}
        }}
    }}
    """
    response = {
        "head": {"vars": ["var"]},
        "results": {"bindings": [{"var": {"type": "literal", "value": "a\tb"}}]},
    }
    function_httpmock.responses[MethodName.GET].append(
        MockHTTPResponse(
            200,
            "OK",
            json.dumps(response).encode("utf-8"),
            {"Content-Type": ["application/sparql-results+json"]},
        )
    )

    Graph().query(query).bindings

    (request,) = function_httpmock.requests[MethodName.GET]
    assert '"a\tb"' in request.path_query["query"][0]


@pytest.mark.parametrize(
    ("query", "service_query"),
    [
        pytest.param(
            "SELECT ?var WHERE {\n"
            "\tSERVICE\t<REMOTE_URL>\t{\n"
            '\t\tSELECT ?var WHERE { VALUES ?var { "x" } }\n'
            "\t}\n"
            "}\n",
            '\n\t\tSELECT ?var WHERE { VALUES ?var { "x" } }\n\t',
            id="tab-indented",
        ),
        pytest.param(
            "SELECT ?var WHERE { SERVICE\t<REMOTE_URL>\t{\t"
            'SELECT ?var WHERE { VALUES ?var { "x" } }\t} }',
            '\tSELECT ?var WHERE { VALUES ?var { "x" } }\t',
            id="tab-mid-line",
        ),
    ],
)
def test_service_tab_whitespace(
    function_httpmock: ServedBaseHTTPServerMock, query: str, service_query: str
) -> None:
    # Tabs used as whitespace in a SERVICE pattern reach the endpoint unchanged.
    query = query.replace("REMOTE_URL", function_httpmock.url)
    function_httpmock.responses[MethodName.GET].append(
        make_select_response({"var": "x"})
    )

    assert Graph().query(query).bindings == [{Variable("var"): Literal("x")}]
    (request,) = function_httpmock.requests[MethodName.GET]
    assert request.path_query["query"] == [service_query]


def make_select_response(*rows: Mapping[str, str]) -> MockHTTPResponse:
    """Make a JSON SELECT result whose rows bind variables to simple literals."""
    response = {
        "head": {"vars": list(dict.fromkeys(var for row in rows for var in row))},
        "results": {
            "bindings": [
                {var: {"type": "literal", "value": value} for var, value in row.items()}
                for row in rows
            ]
        },
    }
    return MockHTTPResponse(
        200,
        "OK",
        json.dumps(response).encode("utf-8"),
        {"Content-Type": ["application/sparql-results+json"]},
    )


@pytest.mark.parametrize(
    ("prologue", "service"),
    [
        pytest.param("", "SERVICE SILENT <REMOTE_URL/sparql> ", id="silent"),
        pytest.param("", "SERVICE<REMOTE_URL/sparql>", id="no-space"),
        pytest.param(
            "",
            "SERVICE <REMOTE_URL/sparql> # {not the pattern}\n",
            id="comment-before-pattern",
        ),
        pytest.param(
            "PREFIX ep: <REMOTE_URL/>", "SERVICE ep:sparql ", id="prefixed-name"
        ),
        pytest.param("BASE <REMOTE_URL/>", "SERVICE <sparql> ", id="relative-iri"),
    ],
)
def test_service_endpoint_forms(
    function_httpmock: ServedBaseHTTPServerMock, prologue: str, service: str
) -> None:
    query = f"""{prologue}
    SELECT ?var WHERE {{
        {service}{{ SELECT ?var WHERE {{ VALUES ?var {{ "x" }} }} }}
    }}
    """
    query = query.replace("REMOTE_URL", function_httpmock.url)
    function_httpmock.responses[MethodName.GET].append(
        make_select_response({"var": "x"})
    )

    assert Graph().query(query).bindings == [{Variable("var"): Literal("x")}]
    (request,) = function_httpmock.requests[MethodName.GET]
    assert request.parsed_path.path == "/sparql"
    assert request.path_query["query"] == [
        ' SELECT ?var WHERE { VALUES ?var { "x" } } '
    ]


@pytest.mark.parametrize(
    ("method", "value"),
    [(MethodName.GET, "x"), (MethodName.POST, "x" * 700)],
    ids=["GET", "POST"],
)
@pytest.mark.parametrize(
    ("endpoint", "endpoint_params"),
    [
        pytest.param("/sparql", {}, id="plain"),
        pytest.param("/sparql?", {}, id="empty-query-string"),
        pytest.param(
            "/sparql?default-graph-uri=http%3A%2F%2Fg",
            {"default-graph-uri": ["http://g"]},
            id="query-string",
        ),
        pytest.param("/sparql#frag", {}, id="fragment"),
        pytest.param("/sparql?a=b#frag", {"a": ["b"]}, id="query-string-and-fragment"),
    ],
)
def test_service_endpoint_parameters(
    function_httpmock: ServedBaseHTTPServerMock,
    method: MethodName,
    value: str,
    endpoint: str,
    endpoint_params: dict[str, list[str]],
) -> None:
    # The endpoint's own parameters are kept, and its fragment is dropped as
    # fragments are never sent over HTTP. The long literal forces POST.
    service_query = f' SELECT ?var WHERE {{ VALUES ?var {{ "{value}" }} }} '
    query = f"""
    SELECT ?var WHERE {{
        SERVICE <{function_httpmock.url}{endpoint}> {{{service_query}}}
    }}
    """
    function_httpmock.responses[method].append(make_select_response({"var": value}))

    assert Graph().query(query).bindings == [{Variable("var"): Literal(value)}]
    service_params = {"query": [service_query], "output": ["json"]}
    (request,) = function_httpmock.requests[method]
    assert request.parsed_path.path == "/sparql"
    if method == MethodName.GET:
        assert request.path_query == {**endpoint_params, **service_params}
    else:
        assert request.path_query == endpoint_params
        assert request.body is not None
        assert parse_qs(request.body.decode()) == service_params


FOAF_PREFIX = "PREFIX foaf: <http://xmlns.com/foaf/0.1/>"


@pytest.mark.parametrize(
    ("prologue", "pattern", "service_query"),
    [
        pytest.param(
            FOAF_PREFIX,
            " SELECT ?var WHERE { ?s foaf:name ?var } ",
            f"{FOAF_PREFIX}  SELECT ?var WHERE {{ ?s foaf:name ?var }} ",
            id="sub-select-prefix",
        ),
        pytest.param(
            "BASE <http://example.org/>",
            " SELECT ?var WHERE { <s> <p> ?var } ",
            "BASE <http://example.org/>  SELECT ?var WHERE { <s> <p> ?var } ",
            id="sub-select-base",
        ),
        pytest.param(
            # rdflib binds the owl and xsd prefixes without a declaration.
            "",
            ' SELECT ?var WHERE { ?s owl:sameAs ?var FILTER(?var != "y"^^xsd:string) } ',
            "PREFIX owl: <http://www.w3.org/2002/07/owl#>"
            " PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> "
            ' SELECT ?var WHERE { ?s owl:sameAs ?var FILTER(?var != "y"^^xsd:string) } ',
            id="sub-select-bound-prefixes",
        ),
        pytest.param(
            f"BASE <http://example.org/> {FOAF_PREFIX}",
            " <s> foaf:name ?var ",
            f"BASE <http://example.org/> {FOAF_PREFIX}"
            " SELECT REDUCED * WHERE { <s> foaf:name ?var }",
            id="bare-pattern",
        ),
        pytest.param(
            f"BASE <http://example.org/> {FOAF_PREFIX}",
            ' SELECT ?var WHERE { VALUES ?var { "x" } } ',
            ' SELECT ?var WHERE { VALUES ?var { "x" } } ',
            id="nothing-used",
        ),
    ],
)
def test_service_query_declares_prefixes_and_base(
    function_httpmock: ServedBaseHTTPServerMock,
    caplog: pytest.LogCaptureFixture,
    prologue: str,
    pattern: str,
    service_query: str,
) -> None:
    # The endpoint gets the prefixes and base the pattern uses, so that its
    # IRIs resolve there as they do here, see
    # https://www.w3.org/TR/sparql11-federated-query/#defn_evalService
    # Declaring only those keeps short queries short enough for GET. The BASE
    # must not make the query an IRI, which logged warnings holding the query.
    caplog.set_level(logging.WARNING)
    query = f"""{prologue}
    SELECT ?var WHERE {{ SERVICE <{function_httpmock.url}/sparql> {{{pattern}}} }}
    """
    function_httpmock.responses[MethodName.GET].append(
        make_select_response({"var": "x"})
    )

    assert Graph().query(query).bindings == [{Variable("var"): Literal("x")}]
    (request,) = function_httpmock.requests[MethodName.GET]
    assert request.path_query["query"] == [service_query]
    assert [record.getMessage() for record in caplog.records] == []


def find_service_patterns(query: str) -> list[CompValue]:
    """Get the SERVICE patterns in the algebra of a query."""
    patterns: list[CompValue] = []

    def collect(node: object) -> None:
        if isinstance(node, CompValue) and node.name == "ServiceGraphPattern":
            patterns.append(node)

    traverse(prepareQuery(query).algebra, visitPost=collect)
    return patterns


def test_service_parse_tree() -> None:
    # Code outside rdflib reads the keys of a SERVICE pattern, service_string
    # among them, so keep them as they are.
    query = """
    SELECT * WHERE {
        SERVICE <http://example.org/a> { ?s ?p ?o }
        SERVICE SILENT <http://example.org/b> { ?o ?q ?r }
    }
    """
    patterns = find_service_patterns(query)

    assert {pattern["service_string"]: sorted(pattern) for pattern in patterns} == {
        "SERVICE <http://example.org/a> { ?s ?p ?o }": [
            "_vars",
            "graph",
            "service_string",
            "term",
        ],
        "SERVICE SILENT <http://example.org/b> { ?o ?q ?r }": [
            "_vars",
            "graph",
            "service_string",
            "silent",
            "term",
        ],
    }


def test_service_string_after_decoy_literal() -> None:
    # A string literal that looks like a SERVICE pattern is not its text.
    query = """
    SELECT * WHERE {
        ?s ?p "SERVICE <http://example.org/decoy> { }" .
        SERVICE <http://example.org/real> { ?a ?b ?c }
    }
    """
    (pattern,) = find_service_patterns(query)

    assert pattern["term"] == URIRef("http://example.org/real")
    assert pattern["service_string"] == "SERVICE <http://example.org/real> { ?a ?b ?c }"


@pytest.mark.parametrize(
    ("prologue", "head"),
    [
        pytest.param(
            "PREFIX ep: <http://example.org/>",
            "SERVICE ep:a\\#b ",
            id="escaped-prefixed-name",
        ),
        pytest.param("", "SERVICE <http://example.org/s#f> ", id="iri-with-hash"),
        pytest.param(
            "", "SERVICE <http://example.org/s>\r\n# { <\r\n", id="comment-after-crlf"
        ),
        pytest.param(
            "", "SERVICE#c\n<http://example.org/s> ", id="comment-after-keyword"
        ),
    ],
)
def test_service_graph_pattern_text(prologue: str, head: str) -> None:
    # The nested group shows if the text is cut at the wrong brace.
    body = " ?s ?p ?o FILTER EXISTS { ?s ?q ?r } "
    (pattern,) = find_service_patterns(
        f"{prologue} SELECT * WHERE {{ {head}{{{body}}} }}"
    )

    assert evaluate._serviceGraphPatternText(pattern) == body


def test_service_string_without_pattern_raises_promptly() -> None:
    # Each comment in this text used to multiply the time taken to find that
    # there is no group graph pattern, which was about 14 seconds for 12.
    service_string = "SERVICE <http://example.org/> " + "# x " * 12
    part = CompValue("ServiceGraphPattern", service_string=service_string)

    start = time.perf_counter()
    with pytest.raises(ValueError, match="no usable service_string"):
        evaluate._serviceGraphPatternText(part)
    assert time.perf_counter() - start < 1


def test_service_converts_rows_lazily(
    function_httpmock: ServedBaseHTTPServerMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Without SILENT, rows past the LIMIT are never converted.
    converted = []
    convert = evaluate._yieldBindingsFromServiceCallResult

    def counting_convert(
        ctx: QueryContext, row: dict[str, dict[str, str]], variables: list[str]
    ) -> Iterator[FrozenBindings]:
        converted.append(row)
        return convert(ctx, row, variables)

    monkeypatch.setattr(
        evaluate, "_yieldBindingsFromServiceCallResult", counting_convert
    )
    query = f"""
    SELECT ?var WHERE {{
        SERVICE <{function_httpmock.url}> {{
            SELECT ?var WHERE {{ VALUES ?var {{ "0" }} }}
        }}
    }} LIMIT 1
    """
    function_httpmock.responses[MethodName.GET].append(
        make_select_response(*({"var": str(index)} for index in range(10)))
    )

    assert Graph().query(query).bindings == [{Variable("var"): Literal("0")}]
    assert len(converted) == 1


def test_service_nested(function_httpmock: ServedBaseHTTPServerMock) -> None:
    # The outer endpoint gets the inner SERVICE pattern as part of its query.
    inner = 'SERVICE <http://example.org/inner> { VALUES ?var { "x" } }'
    query = f"""
    SELECT ?var WHERE {{
        SERVICE <{function_httpmock.url}> {{ SELECT ?var WHERE {{ {inner} }} }}
    }}
    """
    function_httpmock.responses[MethodName.GET].append(
        make_select_response({"var": "x"})
    )

    assert Graph().query(query).bindings == [{Variable("var"): Literal("x")}]
    (request,) = function_httpmock.requests[MethodName.GET]
    assert request.path_query["query"] == [f" SELECT ?var WHERE {{ {inner} }} "]


def test_service_in_update(function_httpmock: ServedBaseHTTPServerMock) -> None:
    # The SERVICE text comes from the second operation of the update.
    graph = Graph()
    function_httpmock.responses[MethodName.GET].append(
        make_select_response({"var": "x"})
    )

    graph.update(
        f"""
        INSERT DATA {{ <urn:ex:a> <urn:ex:p> "a" }} ;
        INSERT {{ <urn:ex:b> <urn:ex:p> ?var }} WHERE {{
            SERVICE <{function_httpmock.url}> {{
                SELECT ?var WHERE {{ VALUES ?var {{ "x" }} }}
            }}
        }}
        """
    )

    assert (URIRef("urn:ex:b"), URIRef("urn:ex:p"), Literal("x")) in graph
    (request,) = function_httpmock.requests[MethodName.GET]
    assert 'VALUES ?var { "x" }' in request.path_query["query"][0]


def test_service_graph_pattern_inside(
    function_httpmock: ServedBaseHTTPServerMock,
) -> None:
    # The endpoint IRI must stop at its own closing angle bracket, not run on
    # to the IRI of the GRAPH pattern inside the SERVICE pattern.
    query = f"""
    SELECT ?var WHERE {{
        SERVICE <{function_httpmock.url}/sparql> {{
            SELECT ?var WHERE {{ GRAPH <http://example.org/g> {{ ?s ?p ?var }} }}
        }}
    }}
    """
    function_httpmock.responses[MethodName.GET].append(
        make_select_response({"var": "x"})
    )

    assert Graph().query(query).bindings == [{Variable("var"): Literal("x")}]
    (request,) = function_httpmock.requests[MethodName.GET]
    assert request.parsed_path.path == "/sparql"
    assert (
        "GRAPH <http://example.org/g> { ?s ?p ?var }" in request.path_query["query"][0]
    )


def test_service_two_patterns(
    function_httpmocks: tuple[ServedBaseHTTPServerMock, ServedBaseHTTPServerMock],
) -> None:
    # Each SERVICE pattern sends its own text to its own endpoint, see
    # https://github.com/RDFLib/rdflib/issues/3069. Two mock servers keep
    # this independent of the order the patterns are evaluated in.
    first, second = function_httpmocks
    query = f"""
    SELECT ?a ?b WHERE {{
        SERVICE <{first.url}/one> {{ SELECT ?a WHERE {{ VALUES ?a {{ "1" }} }} }}
        SERVICE <{second.url}/two> {{ SELECT ?b WHERE {{ VALUES ?b {{ "2" }} }} }}
    }}
    """
    first.responses[MethodName.GET].append(make_select_response({"a": "1"}))
    second.responses[MethodName.GET].append(make_select_response({"b": "2"}))

    assert Graph().query(query).bindings == [
        {Variable("a"): Literal("1"), Variable("b"): Literal("2")}
    ]
    (first_request,) = first.requests[MethodName.GET]
    assert first_request.parsed_path.path == "/one"
    assert 'VALUES ?a { "1" }' in first_request.path_query["query"][0]
    (second_request,) = second.requests[MethodName.GET]
    assert second_request.parsed_path.path == "/two"
    assert 'VALUES ?b { "2" }' in second_request.path_query["query"][0]


# Each failure, with the error it raises without SILENT
ENDPOINT_FAILURES: dict[
    str, tuple[MockHTTPResponse, type[Exception], Optional[str]]
] = {
    "http-error": (
        MockHTTPResponse(500, "Internal Server Error", b"", {}),
        HTTPError,
        "HTTP Error 500",
    ),
    "no-content": (
        MockHTTPResponse(204, "No Content", b"", {}),
        Exception,
        "responded with code: 204",
    ),
    "invalid-json": (
        MockHTTPResponse(
            200,
            "OK",
            b"not json",
            {"Content-Type": ["application/sparql-results+json"]},
        ),
        ValueError,
        None,
    ),
    # Fails on the second row, after the first was converted.
    "invalid-binding": (
        MockHTTPResponse(
            200,
            "OK",
            json.dumps(
                {
                    "head": {"vars": ["var"]},
                    "results": {
                        "bindings": [
                            {"var": {"type": "literal", "value": "x"}},
                            {"var": {"type": "invalid-type"}},
                        ]
                    },
                }
            ).encode("utf-8"),
            {"Content-Type": ["application/sparql-results+json"]},
        ),
        ValueError,
        "invalid type",
    ),
}


@pytest.mark.parametrize("failure", ENDPOINT_FAILURES)
def test_service_silent_ignores_endpoint_failure(
    function_httpmock: ServedBaseHTTPServerMock,
    caplog: pytest.LogCaptureFixture,
    failure: str,
) -> None:
    # A failed SERVICE SILENT pattern gives one solution with no bindings, see
    # https://www.w3.org/TR/sparql11-federated-query/#serviceFailure
    caplog.set_level(logging.DEBUG, logger=evaluate.__name__)
    query = f"""
    SELECT ?kept ?var WHERE {{
        BIND("kept" AS ?kept)
        SERVICE SILENT <{function_httpmock.url}> {{
            SELECT ?var WHERE {{ VALUES ?var {{ "x" }} }}
        }}
    }}
    """
    response, _, _ = ENDPOINT_FAILURES[failure]
    function_httpmock.responses[MethodName.GET].append(response)

    assert Graph().query(query).bindings == [{Variable("kept"): Literal("kept")}]
    assert function_httpmock.call_count == 1
    (record,) = [r for r in caplog.records if r.name == evaluate.__name__]
    assert record.levelno == logging.WARNING
    assert function_httpmock.url in record.getMessage()
    assert isinstance(record.exc_info, tuple)


def test_service_silent_warning_is_one_line(
    function_httpmock: ServedBaseHTTPServerMock, caplog: pytest.LogCaptureFixture
) -> None:
    # A failing endpoint can fail once for each solution it is joined with, so
    # the warning has no traceback unless debug logging is on.
    caplog.set_level(logging.WARNING, logger=evaluate.__name__)
    query = f"""
    SELECT ?var WHERE {{
        SERVICE SILENT <{function_httpmock.url}> {{
            SELECT ?var WHERE {{ VALUES ?var {{ "x" }} }}
        }}
    }}
    """
    response, _, _ = ENDPOINT_FAILURES["http-error"]
    function_httpmock.responses[MethodName.GET].append(response)

    Graph().query(query).bindings
    (record,) = [r for r in caplog.records if r.name == evaluate.__name__]
    assert record.levelno == logging.WARNING
    assert record.getMessage() == (
        f"Ignoring failed SERVICE SILENT call to {function_httpmock.url}: HTTPError"
    )
    assert not record.exc_info


def refuse_requests_to(url: str) -> AuditHookType:
    """Make an audit hook that refuses every request to url, as in
    docs/security_considerations.md."""

    def audit_hook(name: str, args: tuple[Any, ...]) -> None:
        if args[0].startswith(url):
            raise PermissionError("Permission denied for URL")

    return audit_hook


def test_service_silent_refused_by_audit_hook(
    function_httpmock: ServedBaseHTTPServerMock,
    audit_hook_dispatcher: AuditHookDispatcher,
    caplog: pytest.LogCaptureFixture,
) -> None:
    # A request that an audit hook refuses is never sent, and SILENT turns the
    # refusal into a warning.
    caplog.set_level(logging.WARNING, logger=evaluate.__name__)
    query = f"""
    SELECT ?kept ?var WHERE {{
        BIND("kept" AS ?kept)
        SERVICE SILENT <{function_httpmock.url}> {{
            SELECT ?var WHERE {{ VALUES ?var {{ "x" }} }}
        }}
    }}
    """

    with audit_hook_dispatcher.ctx_hook(
        "urllib.Request", refuse_requests_to(function_httpmock.url)
    ):
        bindings = Graph().query(query).bindings

    assert bindings == [{Variable("kept"): Literal("kept")}]
    assert function_httpmock.call_count == 0
    (record,) = [r for r in caplog.records if r.name == evaluate.__name__]
    assert record.levelno == logging.WARNING


def test_service_silent_warning_hides_secrets(
    function_httpmock: ServedBaseHTTPServerMock,
    audit_hook_dispatcher: AuditHookDispatcher,
    caplog: pytest.LogCaptureFixture,
) -> None:
    # The endpoint's userinfo and query string can hold secrets, and so can an
    # error's message, so the warning leaves them out.
    caplog.set_level(logging.WARNING, logger=evaluate.__name__)
    host = function_httpmock.address_string
    endpoint = f"http://user:hunter2@{host}/sparql?apikey=s3cr3t"
    query = f"""
    SELECT ?var WHERE {{
        SERVICE SILENT <{endpoint}> {{
            SELECT ?var WHERE {{ VALUES ?var {{ "x" }} }}
        }}
    }}
    """

    requested = []

    def audit_hook(name: str, args: tuple[Any, ...]) -> None:
        requested.append(args[0])
        raise PermissionError(f"Permission denied for {args[0]}")

    with audit_hook_dispatcher.ctx_hook("urllib.Request", audit_hook):
        Graph().query(query).bindings

    # The request itself is unchanged.
    (url,) = requested
    assert url.startswith(endpoint + "&query=")
    (record,) = [r for r in caplog.records if r.name == evaluate.__name__]
    assert record.getMessage() == (
        f"Ignoring failed SERVICE SILENT call to http://{host}/sparql: PermissionError"
    )


class NoContentHandler(BaseHandler):
    """Answer every HTTP request with 204 No Content, without any network."""

    def http_open(self, req: Request) -> addinfourl:
        return addinfourl(BytesIO(), HTTPMessage(), req.get_full_url(), 204)


def test_service_error_hides_secrets(caplog: pytest.LogCaptureFixture) -> None:
    # rdflib's own error for a 2xx response other than 200 names the endpoint
    # without its userinfo and query, which can hold secrets. urllib cannot
    # send a request with userinfo, so a stub opener gives the 204.
    caplog.set_level(logging.DEBUG, logger=evaluate.__name__)
    endpoint = "http://user:hunter2@example.org/sparql?apikey=s3cr3t"
    opener = OpenerDirector()
    opener.add_handler(NoContentHandler())

    with context_urlopener(opener):
        with pytest.raises(Exception, match="responded with code: 204") as raised:
            Graph().query(
                f"SELECT * WHERE {{ SERVICE <{endpoint}> {{ ?s ?p ?o }} }}"
            ).bindings
        Graph().query(
            f"SELECT * WHERE {{ SERVICE SILENT <{endpoint}> {{ ?s ?p ?o }} }}"
        ).bindings

    message = "Service: http://example.org/sparql responded with code: 204"
    assert str(raised.value) == message
    assert message in caplog.text
    assert "hunter2" not in caplog.text
    assert "s3cr3t" not in caplog.text


def test_service_refused_by_audit_hook_raises(
    function_httpmock: ServedBaseHTTPServerMock,
    audit_hook_dispatcher: AuditHookDispatcher,
) -> None:
    query = f"""
    SELECT ?var WHERE {{
        SERVICE <{function_httpmock.url}> {{
            SELECT ?var WHERE {{ VALUES ?var {{ "x" }} }}
        }}
    }}
    """

    with audit_hook_dispatcher.ctx_hook(
        "urllib.Request", refuse_requests_to(function_httpmock.url)
    ):
        with pytest.raises(PermissionError, match="Permission denied for URL"):
            Graph().query(query).bindings
    assert function_httpmock.call_count == 0


def refusing_opener(url: str) -> OpenerDirector:
    """Make a URL opener that refuses every request to url, as in
    docs/security_considerations.md."""

    class RefusingHTTPHandler(HTTPHandler):
        def http_open(self, req: Request) -> HTTPResponse:
            if req.get_full_url().startswith(url):
                raise PermissionError("Permission denied for URL")
            return super().http_open(req)

    opener = OpenerDirector()
    opener.add_handler(RefusingHTTPHandler())
    return opener


def test_service_silent_refused_by_opener(
    function_httpmock: ServedBaseHTTPServerMock, caplog: pytest.LogCaptureFixture
) -> None:
    # A request that a custom URL opener refuses is never sent, and SILENT
    # turns the refusal into a warning.
    caplog.set_level(logging.WARNING, logger=evaluate.__name__)
    query = f"""
    SELECT ?kept ?var WHERE {{
        BIND("kept" AS ?kept)
        SERVICE SILENT <{function_httpmock.url}> {{
            SELECT ?var WHERE {{ VALUES ?var {{ "x" }} }}
        }}
    }}
    """

    with context_urlopener(refusing_opener(function_httpmock.url)):
        bindings = Graph().query(query).bindings

    assert bindings == [{Variable("kept"): Literal("kept")}]
    assert function_httpmock.call_count == 0
    (record,) = [r for r in caplog.records if r.name == evaluate.__name__]
    assert record.levelno == logging.WARNING


def test_service_refused_by_opener_raises(
    function_httpmock: ServedBaseHTTPServerMock,
) -> None:
    query = f"""
    SELECT ?var WHERE {{
        SERVICE <{function_httpmock.url}> {{
            SELECT ?var WHERE {{ VALUES ?var {{ "x" }} }}
        }}
    }}
    """

    with context_urlopener(refusing_opener(function_httpmock.url)):
        with pytest.raises(PermissionError, match="Permission denied for URL"):
            Graph().query(query).bindings
    assert function_httpmock.call_count == 0


@pytest.mark.parametrize("failure", ENDPOINT_FAILURES)
def test_service_endpoint_failure_raises(
    function_httpmock: ServedBaseHTTPServerMock, failure: str
) -> None:
    query = f"""
    SELECT ?var WHERE {{
        SERVICE <{function_httpmock.url}> {{
            SELECT ?var WHERE {{ VALUES ?var {{ "x" }} }}
        }}
    }}
    """
    response, error, match = ENDPOINT_FAILURES[failure]
    function_httpmock.responses[MethodName.GET].append(response)

    with pytest.raises(error, match=match):
        Graph().query(query).bindings
    assert function_httpmock.call_count == 1


@pytest.mark.parametrize(
    "failure",
    [None, *(failure for failure in ENDPOINT_FAILURES if failure != "http-error")],
)
def test_service_closes_response(
    function_httpmock: ServedBaseHTTPServerMock,
    monkeypatch: pytest.MonkeyPatch,
    failure: Optional[str],
) -> None:
    # The response is closed whether or not the call succeeds. urllib raises
    # an HTTP error status itself, so rdflib never gets that response.
    opened = []

    def recording_urlopen(request: Request) -> HTTPResponse:
        response = urlopen(request)
        opened.append(response)
        return response

    monkeypatch.setattr(evaluate, "urlopen", recording_urlopen)
    query = f"""
    SELECT ?var WHERE {{
        SERVICE <{function_httpmock.url}> {{
            SELECT ?var WHERE {{ VALUES ?var {{ "x" }} }}
        }}
    }}
    """
    if failure is None:
        function_httpmock.responses[MethodName.GET].append(
            make_select_response({"var": "x"})
        )
        assert Graph().query(query).bindings == [{Variable("var"): Literal("x")}]
    else:
        response, error, match = ENDPOINT_FAILURES[failure]
        function_httpmock.responses[MethodName.GET].append(response)
        with pytest.raises(error, match=match):
            Graph().query(query).bindings

    (response,) = opened
    assert response.closed


@pytest.mark.parametrize("silent", ["", "SILENT"])
def test_service_variable_endpoint_raises(silent: str) -> None:
    # A variable endpoint is not supported, so it must not quietly give no
    # solutions.
    query = f"""
    SELECT ?var WHERE {{
        SERVICE {silent} ?endpoint {{
            SELECT ?var WHERE {{ VALUES ?var {{ "x" }} }}
        }}
    }}
    """

    with pytest.raises(ValueError, match="the endpoint must be an IRI"):
        Graph().query(query).bindings


def test_service_pattern_without_text_raises() -> None:
    part = CompValue("ServiceGraphPattern", term=URIRef("http://example.org/"))

    with pytest.raises(ValueError, match="no usable service_string"):
        next(evaluate.evalServiceQuery(QueryContext(Graph()), part))


if __name__ == "__main__":
    test_service()
    test_service_with_bind()
    test_service_with_bound_solutions()
    test_service_with_values()
    test_service_with_implicit_select()
    test_service_with_implicit_select_and_prefix()
    test_service_with_implicit_select_and_base()
    test_service_node_types()
