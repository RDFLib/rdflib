from rdflib import Graph, URIRef, Literal, Variable
from rdflib.plugins.sparql import prepareQuery
from rdflib.compare import isomorphic

from . import helper


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
      service <http://DBpedia.org/sparql>
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
      service <http://DBpedia.org/sparql>
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
      service <http://DBpedia.org/sparql>
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
      SERVICE <http://dbpedia.org/sparql>
      {
        ?s <http://www.w3.org/2002/07/owl#sameAs> ?sameAs .
      }
    } LIMIT 3"""
    results = helper.query_with_retry(g, q)
    assert len(results) == 3


# def test_with_fixture(httpserver):
#    httpserver.expect_request("/sparql/?query=SELECT * WHERE ?s ?p ?o").respond_with_json({"vars": ["s","p","o"], "bindings":[]})
#    test_server = httpserver.url_for('/sparql')
#    g = Graph()
#    q = 'SELECT * WHERE {SERVICE <'+test_server+'>{?s ?p ?o} . ?s ?p ?o .}'
#    results = g.query(q)
#   assert len(results) == 0


if __name__ == "__main__":
    # import nose
    # nose.main(defaultTest=__name__)
    test_service()
    test_service_with_bind()
    test_service_with_values()
    test_service_with_implicit_select()
    test_service_with_implicit_select_and_prefix()
    test_service_with_implicit_select_and_base()
