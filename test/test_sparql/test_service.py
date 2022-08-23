import json
from contextlib import ExitStack
from test.utils import helper
from test.utils.httpservermock import (
    MethodName,
    MockHTTPResponse,
    ServedBaseHTTPServerMock,
)
from typing import (
    Dict,
    FrozenSet,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)

import pytest

from rdflib import Graph, Literal, URIRef, Variable
from rdflib.namespace import XSD
from rdflib.term import BNode, Identifier


def test_service():
    g = Graph()
    q = """select ?sameAs ?dbpComment
    where
    { service <http://DBpedia.org/sparql>
    { select ?dbpHypernym ?dbpComment
    where
    {
    <http://dbpedia.org/resource/John_Lilburne>
        <http://www.w3.org/2002/07/owl#sameAs> ?sameAs ;
        <http://www.w3.org/2000/01/rdf-schema#comment> ?dbpComment .

    } }  } limit 2"""
    results = helper.query_with_retry(g, q)
    print(results.vars)
    print(results.bindings)
    assert len(results) == 2

    for r in results:
        assert len(r) == 2


def test_service_with_bind():
    g = Graph()
    q = """select ?sameAs ?dbpComment ?subject
    where
    { bind (<http://dbpedia.org/resource/Category:1614_births> as ?subject)
      service <http://DBpedia.org/sparql>
    { select ?sameAs ?dbpComment ?subject
    where
    {
    <http://dbpedia.org/resource/John_Lilburne>
        <http://www.w3.org/2002/07/owl#sameAs> ?sameAs ;
        <http://www.w3.org/2000/01/rdf-schema#comment> ?dbpComment ;
        <http://purl.org/dc/terms/subject> ?subject .

    } }  } limit 2"""
    results = helper.query_with_retry(g, q)
    assert len(results) == 2

    for r in results:
        assert len(r) == 3


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
        SELECT ?sameAs ?dbpComment ?subject WHERE {
          []
            <http://www.w3.org/2002/07/owl#sameAs> ?sameAs ;
            <http://purl.org/dc/terms/subject> ?subject .

          SERVICE <http://DBpedia.org/sparql> {
            SELECT ?sameAs ?dbpComment ?subject WHERE {
              <http://dbpedia.org/resource/John_Lilburne>
                <http://www.w3.org/2002/07/owl#sameAs> ?sameAs ;
                <http://www.w3.org/2000/01/rdf-schema#comment> ?dbpComment ;
                <http://purl.org/dc/terms/subject> ?subject .
            }
          }
        }
        LIMIT 2
        """
    results = helper.query_with_retry(g, q)
    assert len(results) == 2

    for r in results:
        assert len(r) == 3


def test_service_with_values():
    g = Graph()
    q = """select ?sameAs ?dbpComment ?subject
    where
    { values (?sameAs ?subject) {(<http://de.dbpedia.org/resource/John_Lilburne> <http://dbpedia.org/resource/Category:1614_births>) (<https://global.dbpedia.org/id/4t6Fk> <http://dbpedia.org/resource/Category:Levellers>)}
      service <http://DBpedia.org/sparql>
    { select ?sameAs ?dbpComment ?subject
    where
    {
    <http://dbpedia.org/resource/John_Lilburne>
        <http://www.w3.org/2002/07/owl#sameAs> ?sameAs ;
        <http://www.w3.org/2000/01/rdf-schema#comment> ?dbpComment ;
        <http://purl.org/dc/terms/subject> ?subject .

    } }  } limit 2"""
    results = helper.query_with_retry(g, q)
    assert len(results) == 2

    for r in results:
        assert len(r) == 3


def test_service_with_implicit_select():
    g = Graph()
    q = """select ?s ?p ?o
    where
    {
      service <https://DBpedia.org/sparql>
    {
      values (?s ?p ?o) {(<http://example.org/a> <http://example.org/b> 1) (<http://example.org/a> <http://example.org/b> 2)}
    }} limit 2"""
    results = helper.query_with_retry(g, q)
    assert len(results) == 2

    for r in results:
        assert len(r) == 3


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
    results = helper.query_with_retry(g, q)
    assert len(results) == 2

    for r in results:
        assert len(r) == 3


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
    results = helper.query_with_retry(g, q)
    assert len(results) == 2

    for r in results:
        assert len(r) == 3


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
    results = helper.query_with_retry(g, q)
    assert len(results) == 3


def freeze_bindings(
    bindings: Sequence[Mapping[Variable, Identifier]]
) -> FrozenSet[FrozenSet[Tuple[Variable, Identifier]]]:
    result = []
    for binding in bindings:
        result.append(frozenset(((key, value)) for key, value in binding.items()))
    return frozenset(result)


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
    results = helper.query_with_retry(g, q)
    assert results.bindings[0].get(Variable("o")) == Literal("c")


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
    results = helper.query_with_retry(g, q)

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
    response_bindings: List[Dict[str, str]],
    expected_result: Union[List[Identifier], Type[Exception]],
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
    function_httpmock.responses[MethodName.GET].append(
        MockHTTPResponse(
            200,
            "OK",
            json.dumps(response).encode("utf-8"),
            {"Content-Type": ["application/sparql-results+json"]},
        )
    )
    catcher: Optional[pytest.ExceptionInfo[Exception]] = None

    with ExitStack() as xstack:
        if isinstance(expected_result, type) and issubclass(expected_result, Exception):
            catcher = xstack.enter_context(pytest.raises(expected_result))
        else:
            expected_bindings = [{Variable("var"): item} for item in expected_result]
        bindings = graph.query(query).bindings
    if catcher is not None:
        assert catcher is not None
        assert catcher.value is not None
    else:
        assert expected_bindings == bindings


if __name__ == "__main__":
    test_service()
    test_service_with_bind()
    test_service_with_bound_solutions()
    test_service_with_values()
    test_service_with_implicit_select()
    test_service_with_implicit_select_and_prefix()
    test_service_with_implicit_select_and_base()
    test_service_node_types()
