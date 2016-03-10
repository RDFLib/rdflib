from __future__ import print_function

from rdflib import *
from rdflib.collection import Collection

def test_issue604():

    EX = Namespace('http://ex.co/')
    g = Graph()
    bn = BNode()
    g.add((EX.s, EX.p, bn))
    c = Collection(g, bn, map(Literal, [1,2,4]))
    c[2] = Literal(3)
    got = list(g.objects(bn, RDF.rest/RDF.rest/RDF.first))
    expected = [ Literal(3) ]
    assert got == [ Literal(3) ], got

