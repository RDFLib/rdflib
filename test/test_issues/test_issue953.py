from fractions import Fraction

from rdflib import Literal, URIRef


def test_issue_939():
    lit = Literal(Fraction("2/3"))
    assert lit.datatype == URIRef("http://www.w3.org/2002/07/owl#rational")
    assert lit.n3() == '"2/3"^^<http://www.w3.org/2002/07/owl#rational>'
