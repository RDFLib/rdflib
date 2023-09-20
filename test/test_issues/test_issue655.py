from decimal import Decimal

from rdflib import XSD, Graph, Literal, Namespace, URIRef
from rdflib.compare import to_isomorphic


def test_issue655():
    # make sure that inf and nan are serialized correctly
    dt = XSD["double"].n3()
    assert Literal(float("inf"))._literal_n3(True) == '"INF"^^%s' % dt
    assert Literal(float("-inf"))._literal_n3(True) == '"-INF"^^%s' % dt
    assert Literal(float("nan"))._literal_n3(True) == '"NaN"^^%s' % dt

    dt = XSD["decimal"].n3()
    assert Literal(Decimal("inf"))._literal_n3(True) == '"INF"^^%s' % dt
    assert Literal(Decimal("-inf"))._literal_n3(True) == '"-INF"^^%s' % dt
    assert Literal(Decimal("nan"))._literal_n3(True) == '"NaN"^^%s' % dt

    assert Literal("inf", datatype=XSD["decimal"])._literal_n3(True) == '"INF"^^%s' % dt

    # assert that non-numerical aren't changed
    assert Literal("inf")._literal_n3(True) == '"inf"'
    assert Literal("nan")._literal_n3(True) == '"nan"'

    PROV = Namespace("http://www.w3.org/ns/prov#")  # noqa: N806

    bob = URIRef("http://example.org/object/Bob")

    # g1 is a simple graph with an infinite and a nan values
    g1 = Graph()
    g1.add((bob, PROV.value, Literal(float("inf"))))
    g1.add((bob, PROV.value, Literal(float("nan"))))

    # Build g2 out of the deserialisation of g1 serialisation
    g2 = Graph()
    g2.parse(data=g1.serialize(format="turtle"), format="turtle")

    assert to_isomorphic(g1) == to_isomorphic(g2)
