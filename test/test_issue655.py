from decimal import Decimal
import unittest
from rdflib import Graph, Namespace, URIRef, Literal, XSD
from rdflib.compare import to_isomorphic


class TestIssue655(unittest.TestCase):

    def test_issue655(self):
        # make sure that inf and nan are serialized correctly
        dt = XSD['double'].n3()
        self.assertEqual(
            Literal(float("inf"))._literal_n3(True),
            '"INF"^^%s' % dt
        )
        self.assertEqual(
            Literal(float("-inf"))._literal_n3(True),
            '"-INF"^^%s' % dt
        )
        self.assertEqual(
            Literal(float("nan"))._literal_n3(True),
            '"NaN"^^%s' % dt
        )

        dt = XSD['decimal'].n3()
        self.assertEqual(
            Literal(Decimal("inf"))._literal_n3(True),
            '"INF"^^%s' % dt
        )
        self.assertEqual(
            Literal(Decimal("-inf"))._literal_n3(True),
            '"-INF"^^%s' % dt
        )
        self.assertEqual(
            Literal(Decimal("nan"))._literal_n3(True),
            '"NaN"^^%s' % dt
        )

        self.assertEqual(
            Literal("inf", datatype=XSD['decimal'])._literal_n3(True),
            '"INF"^^%s' % dt
        )

        # assert that non-numerical aren't changed
        self.assertEqual(
            Literal('inf')._literal_n3(True),
            '"inf"'
        )
        self.assertEqual(
            Literal('nan')._literal_n3(True),
            '"nan"'
        )

        PROV = Namespace('http://www.w3.org/ns/prov#')

        bob = URIRef("http://example.org/object/Bob")

        # g1 is a simple graph with an infinite and a nan values
        g1 = Graph()
        g1.add((bob, PROV.value, Literal(float("inf"))))
        g1.add((bob, PROV.value, Literal(float("nan"))))

        # Build g2 out of the deserialisation of g1 serialisation
        g2 = Graph()
        g2.parse(data=g1.serialize(format='turtle'), format='turtle')

        self.assertTrue(to_isomorphic(g1) == to_isomorphic(g2))


if __name__ == "__main__":
    unittest.main()
