# test for https://github.com/RDFLib/rdflib/issues/607

from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import FOAF, RDF

X = Namespace("http://example.org/")

sample_data = '''
@prefix x: <http://example.org/> .

x:a x:p x:b .
x:b x:p x:c .
x:x x:p x:y .
'''

g = Graph().parse(data=sample_data, format='n3')
assert len(g) == 3


# find 2 hop chain (this works)
q = '''
select ?a ?b ?c where {
  ?a x:p ?b .
  ?b x:p ?c .
}
'''
expected = [(X.a, X.b, X.c)]
res = sorted(g.query(q))
assert res == expected, '\nexpected: %s\ngot     : %s' % (expected, res)


# find 2 hop chain with subquery (doesn't work)
q = '''
select ?a ?b ?c where {
  ?a x:p ?b .
  {
    select ?b ?c where {
      ?b x:p ?c .
    }
  }
}
'''
res = sorted(g.query(q))
assert res == expected, '\nexpected: %s\ngot     : %s' % (expected, res)


# find 2 hop chain with subquery, exec subquery first (works)
q = '''
select ?a ?b ?c where {
  {
    select ?b ?c where {
      ?b x:p ?c .
    }
  }
  ?a x:p ?b .
}
'''
res = sorted(g.query(q))
assert res == expected, '\nexpected: %s\ngot     : %s' % (expected, res)
