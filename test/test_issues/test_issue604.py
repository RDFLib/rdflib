from rdflib import RDF, BNode, Graph, Literal, Namespace
from rdflib.collection import Collection


def test_issue604():
    EX = Namespace("http://ex.co/")  # noqa: N806
    g = Graph()
    bn = BNode()
    g.add((EX.s, EX.p, bn))
    c = Collection(g, bn, map(Literal, [1, 2, 4]))
    c[2] = Literal(3)
    got = list(g.objects(bn, RDF.rest / RDF.rest / RDF.first))
    expected = [Literal(3)]  # noqa: F841
    assert got == [Literal(3)], got
