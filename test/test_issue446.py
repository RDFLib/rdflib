# coding=utf-8
# test for https://github.com/RDFLib/rdflib/issues/446

from rdflib import Graph, URIRef, Literal

def test_sparql_unicode():
    g = Graph()
    trip = (
        URIRef('http://example.org/foo'),
        URIRef('http://example.org/bar'),
        URIRef(u'http://example.org/jörn')
    )
    g.add(trip)
    q = 'select ?s ?p ?o where { ?s ?p ?o . FILTER(lang(?o) = "") }'
    r = list(g.query(q))
    assert r == [], \
        'sparql query %r should return nothing but returns %r' % (q, r)


if __name__ == '__main__':
    test_sparql_unicode()
