from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.compare import to_isomorphic
import unittest


class TestIssue655(unittest.TestCase):

    def test_issue655(self):
        PROV = Namespace('http://www.w3.org/ns/prov#')

        bob = URIRef("http://example.org/object/Bob")
        value = Literal(float("inf"))

        # g1 is a simple graph with one attribute having an infinite value
        g1 = Graph()
        g1.add((bob, PROV.value, value))

        # Build g2 out of the deserialisation of g1 serialisation
        g2 = Graph()
        g2.parse(data=g1.serialize(format='turtle'), format='turtle')

        self.assertTrue(g1.serialize(
            format='turtle') == g2.serialize(format='turtle'))
        self.assertTrue(to_isomorphic(g1) == to_isomorphic(g2))

if __name__ == "__main__":
    unittest.main()
