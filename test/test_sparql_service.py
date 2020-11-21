import time
import urllib.error

from rdflib import Graph, URIRef, Literal, Variable
from rdflib.plugins.sparql import prepareQuery
from rdflib.compare import isomorphic

MAX_RETRY = 3
def run_query_and_retry_on_network_error(graph, query):
    backoff = 0
    for i in range(MAX_RETRY):
        try:
            result = graph.query(query)
            result.bindings # access bindings to ensure no lazy loading
            return result
        except urllib.error.URLError as e:
            if i == MAX_RETRY -1:
              raise e

            backoff_s = 1.2 ** backoff
            print(f"Network eroror {e} during query, waiting for {backoff_s}s and retrying")
            time.sleep(1)
            backoff += 1


def test_service():
    g = Graph()
    q = """select ?dbpHypernym ?dbpComment
    where
    { service <http://DBpedia.org/sparql>
    { select ?dbpHypernym ?dbpComment
    where
    {
    <http://dbpedia.org/resource/John_Lilburne>
        <http://purl.org/linguistics/gold/hypernym> ?dbpHypernym ;
        <http://www.w3.org/2000/01/rdf-schema#comment> ?dbpComment .

    } }  } limit 2"""
    results = run_query_and_retry_on_network_error(g, q)
    assert len(results) == 2

    for r in results:
        assert len(r) == 2


def test_service_with_bind():
    g = Graph()
    q = """select ?dbpHypernym ?dbpComment ?dbpDeathPlace
    where
    { bind (<http://dbpedia.org/resource/Eltham> as ?dbpDeathPlace)
      service <http://DBpedia.org/sparql>
    { select ?dbpHypernym ?dbpComment ?dbpDeathPlace
    where
    {
    <http://dbpedia.org/resource/John_Lilburne>
        <http://purl.org/linguistics/gold/hypernym> ?dbpHypernym ;
        <http://www.w3.org/2000/01/rdf-schema#comment> ?dbpComment ;
        <http://dbpedia.org/ontology/deathPlace> ?dbpDeathPlace .

    } }  } limit 2"""
    results = run_query_and_retry_on_network_error(g, q)
    assert len(results) == 2

    for r in results:
        assert len(r) == 3


def test_service_with_values():
    g = Graph()
    q = """select ?dbpHypernym ?dbpComment ?dbpDeathPlace
    where
    { values (?dbpHypernym ?dbpDeathPlace) {(<http://dbpedia.org/resource/Leveller> <http://dbpedia.org/resource/London>) (<http://dbpedia.org/resource/Leveller> <http://dbpedia.org/resource/Eltham>)}
      service <http://DBpedia.org/sparql>
    { select ?dbpHypernym ?dbpComment ?dbpDeathPlace
    where
    {
    <http://dbpedia.org/resource/John_Lilburne>
        <http://purl.org/linguistics/gold/hypernym> ?dbpHypernym ;
        <http://www.w3.org/2000/01/rdf-schema#comment> ?dbpComment ;
        <http://dbpedia.org/ontology/deathPlace> ?dbpDeathPlace .

    } }  } limit 2"""
    results = run_query_and_retry_on_network_error(g, q)
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
    results = run_query_and_retry_on_network_error(g, q)
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
    results = run_query_and_retry_on_network_error(g, q)
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
    results = run_query_and_retry_on_network_error(g, q)
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
        ?s <http://purl.org/linguistics/gold/hypernym> <http://dbpedia.org/resource/Leveller> .
      }
    } LIMIT 3"""
    results = run_query_and_retry_on_network_error(g, q)
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
