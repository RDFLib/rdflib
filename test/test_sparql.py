from rdflib import Graph, URIRef, Literal
from rdflib.plugins.sparql import prepareQuery
from rdflib.compare import isomorphic

from nose.tools import eq_

def test_graph_prefix():
    """
    This is issue https://github.com/RDFLib/rdflib/issues/313
    """

    g1 = Graph()
    g1.parse(data="""
    @prefix : <urn:ns1:> .
    :foo <p> 42.
    """, format="n3")

    g2 = Graph()
    g2.parse(data="""
    @prefix : <urn:somethingelse:> .
    <urn:ns1:foo> <p> 42.
    """, format="n3")

    assert isomorphic(g1, g2)

    q_str = ("""
    PREFIX : <urn:ns1:>
    SELECT ?val
    WHERE { :foo ?p ?val }
    """)
    q_prepared = prepareQuery(q_str)

    expected = [(Literal(42),)]

    eq_(list(g1.query(q_prepared)), expected)
    eq_(list(g2.query(q_prepared)), expected)

    eq_(list(g1.query(q_str)), expected)
    eq_(list(g2.query(q_str)), expected)

def test_variable_order():

    g = Graph()
    g.add((URIRef("http://foo"),URIRef("http://bar"),URIRef("http://baz")))
    res = g.query("SELECT (42 AS ?a) ?b { ?b ?c ?d }")

    row = list(res)[0]
    print(row)
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

def test_complex_sparql_construct():

    g = Graph()
    q = '''select ?subject ?study ?id where {
    ?s a <urn:Person>;
      <urn:partOf> ?c;
      <urn:hasParent> ?mother, ?father;
      <urn:id> [ a <urn:Identifier>; <urn:has-value> ?id].
    }'''
    g.query(q)

if __name__ == '__main__':
    import nose
    nose.main(defaultTest=__name__)
