from fractions import Fraction

from rdflib import Graph, ConjunctiveGraph, Literal, URIRef
import unittest


class TestIssue953(unittest.TestCase):
    def test_issue_939(self):
        lit = Literal(Fraction("2/3"))
        assert lit.datatype == URIRef("http://www.w3.org/2002/07/owl#rational")
        assert lit.n3() == '"2/3"^^<http://www.w3.org/2002/07/owl#rational>'


if __name__ == "__main__":
    unittest.main()
