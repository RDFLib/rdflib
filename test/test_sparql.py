from rdflib import Graph, URIRef, Literal
from rdflib.plugins.sparql import prepareQuery

def test_variable_order(): 
    
    g = Graph()
    g.add((URIRef("http://foo"),URIRef("http://bar"),URIRef("http://baz")))
    res = g.query("SELECT (42 AS ?a) ?b { ?b ?c ?d }")
    
    row = list(res)[0]
    print row
    assert len(row) == 2
    assert row[0] == Literal(42)
    assert row[1] == URIRef("http://foo")


def test_sparql_bnodelist(): 
    """

    syntax tests for a few corner-cases not touched by the 
    official tests.

    """
    
    prepareQuery('select * where { ?s ?p ( [] ) . }')
    prepareQuery('select * where { ?s ?p ( [ ?p2 ?o2 ] ) . }')
    prepareQuery('select * where { ?s ?p ( [ ?p2 ?o2 ] [] ) . }')
    prepareQuery('select * where { ?s ?p ( [] [ ?p2 ?o2 ] [] ) . }')
    
    

    
