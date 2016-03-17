# test for https://github.com/RDFLib/rdflib/issues/580

from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import FOAF, RDF


sample_data = '''
@prefix s: <http://schema.org/> .
@prefix x: <http://example.org/> .

x:john a s:Person ; s:name "John" .
x:jane a s:Person ; s:name "Jane" ; s:knows x:john.
x:ecorp a s:Organization ; s:name "Evil Corp" ; s:employee x:jane .
'''

g = Graph().parse(data=sample_data, format='n3')
assert len(g) == 8

simple_query = '''
select ?s ?o ?x where {
  ?x s:knows ?o .
  BIND(?x as ?s)
}
'''
expected = [
    (
        URIRef(u'http://example.org/jane'),
        URIRef(u'http://example.org/john'),
        URIRef(u'http://example.org/jane'),
    ),
]
res = sorted(g.query(simple_query))
assert res == expected, '\nexpected: %s\ngot     : %s' % (expected, res)


simple_problematic_query = '''
select ?s ?o ?x where {
  ?x s:knows ?o .
  { BIND(?x as ?s) }
}
'''
res = sorted(g.query(simple_problematic_query))
assert res == expected, '\nexpected: %s\ngot     : %s' % (expected, res)


query = '''
#CONSTRUCT { ?s ?p ?o }
SELECT ?s ?p ?o ?x # for debugging
WHERE {
  ?x a s:Person .
  { ?x ?p ?o . BIND (?x as ?s) } UNION
  { ?s ?p ?x . BIND (?x as ?o) }
}
'''
expected = [
    (
        URIRef(u'http://example.org/ecorp'),
        URIRef(u'http://schema.org/employee'),
        URIRef(u'http://example.org/jane'),
        URIRef(u'http://example.org/jane'),
    ), (
        URIRef(u'http://example.org/jane'),
        URIRef(u'http://schema.org/knows'),
        URIRef(u'http://example.org/john'),
        URIRef(u'http://example.org/jane'),
    ), (
        URIRef(u'http://example.org/jane'),
        URIRef(u'http://schema.org/knows'),
        URIRef(u'http://example.org/john'),
        URIRef(u'http://example.org/john'),
    ), (
        URIRef(u'http://example.org/jane'),
        URIRef(u'http://schema.org/name'),
        Literal(u'Jane'),
        URIRef(u'http://example.org/jane'),
    ), (
        URIRef(u'http://example.org/jane'),
        URIRef(u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
        URIRef(u'http://schema.org/Person'),
        URIRef(u'http://example.org/jane'),
    ), (
        URIRef(u'http://example.org/john'),
        URIRef(u'http://schema.org/name'),
        Literal(u'John'),
        URIRef(u'http://example.org/john'),
    ), (
        URIRef(u'http://example.org/john'),
        URIRef(u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
        URIRef(u'http://schema.org/Person'),
        URIRef(u'http://example.org/john'),
    ),
]
res = sorted(g.query(query))
assert res == expected, '\nexpected: %s\ngot     : %s' % (expected, res)

