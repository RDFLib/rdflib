from rdflib import Graph
from rdflib.compare import to_isomorphic
import unittest


class TestIssuexxx(unittest.TestCase):

    def test_graph_equivalence(self):
        g1_ttl = """
        @prefix prov: <http://www.w3.org/ns/prov#> .
        @prefix ex: <http://example.org/#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

        ex:Bob prov:label "Bob"^^xsd:string ;
               prov:value "10.0"^^xsd:double .
        """
        g1 = Graph()
        g1.parse(data=g1_ttl, format='turtle')

        g2_ttl = """
        @prefix prov: <http://www.w3.org/ns/prov#> .
        @prefix ex: <http://example.org/#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

        ex:Bob prov:label "Bob" ;
               prov:value 10E0.0 .
        """
        g2 = Graph()
        g2.parse(data=g2_ttl, format='turtle')

        self.assertTrue(to_isomorphic(g1) == to_isomorphic(g2))

if __name__ == "__main__":
    unittest.main()
