from __future__ import annotations

from rdflib import OWL, RDF, XSD, Graph, Literal, Namespace
from rdflib.extras.infixowl import CastClass, Class, Restriction

EX = Namespace("http://example.org/vocab/")


def _setup_graph() -> Graph:
    g = Graph()
    g.bind("ex", EX, override=False)
    return g


def test_qualified_cardinality_restriction() -> None:
    g = _setup_graph()
    parent = Class(EX.Parent, graph=g)
    r = Restriction(
        EX.hasChild,
        graph=g,
        qualifiedCardinality=Literal(3, datatype=XSD.nonNegativeInteger),
        onClass=parent,
    )

    assert (r.identifier, RDF.type, OWL.Restriction) in g
    assert (r.identifier, OWL.onProperty, EX.hasChild) in g
    assert (
        r.identifier,
        OWL.qualifiedCardinality,
        Literal(3, datatype=XSD.nonNegativeInteger),
    ) in g
    assert (r.identifier, OWL.onClass, EX.Parent) in g
    assert r.restrictionKind() == "qualifiedCardinality"
    assert r.qualifiedCardinality is not None
    assert r.qualifiedCardinality.identifier == Literal(
        3, datatype=XSD.nonNegativeInteger
    )
    assert r.onClass == Class(EX.Parent, graph=g)
    assert str(r) == "( ex:hasChild EQUALS 3 ex:Parent )"

    reloaded = CastClass(r.identifier, graph=g)
    assert isinstance(reloaded, Restriction)
    assert reloaded.restrictionKind() == "qualifiedCardinality"
    assert reloaded.onClass == Class(EX.Parent, graph=g)


def test_max_min_qualified_cardinality_properties_and_syntax() -> None:
    g = _setup_graph()
    r_max = Restriction(
        EX.hasChild,
        graph=g,
        maxQualifiedCardinality=Literal(5, datatype=XSD.nonNegativeInteger),
        onClass=EX.Parent,
    )
    assert r_max.restrictionKind() == "maxQualifiedCardinality"
    assert r_max.maxQualifiedCardinality is not None
    assert str(r_max) == "( ex:hasChild MAX 5 ex:Parent )"

    r_max.maxQualifiedCardinality = Literal(4, datatype=XSD.nonNegativeInteger)
    r_max.onClass = Class(EX.Adult, graph=g)
    assert str(r_max) == "( ex:hasChild MAX 4 ex:Adult )"

    r_min = Restriction(
        EX.hasChild,
        graph=g,
        minQualifiedCardinality=Literal(1, datatype=XSD.nonNegativeInteger),
        onClass=EX.Parent,
    )
    assert r_min.restrictionKind() == "minQualifiedCardinality"
    assert r_min.minQualifiedCardinality is not None
    assert str(r_min) == "( ex:hasChild MIN 1 ex:Parent )"

    del r_min.onClass
    assert r_min.onClass is None
    assert str(r_min) == "( ex:hasChild MIN 1 )"

    del r_min.minQualifiedCardinality
    assert r_min.minQualifiedCardinality is None

    del r_max.maxQualifiedCardinality
    assert r_max.maxQualifiedCardinality is None

    r_exact = Restriction(
        EX.hasChild,
        graph=g,
        qualifiedCardinality=Literal(2, datatype=XSD.nonNegativeInteger),
        onClass=EX.Parent,
    )
    r_exact.qualifiedCardinality = Literal(3, datatype=XSD.nonNegativeInteger)
    assert (
        r_exact.identifier,
        OWL.qualifiedCardinality,
        Literal(3, datatype=XSD.nonNegativeInteger),
    ) in g
    del r_exact.qualifiedCardinality
    assert r_exact.qualifiedCardinality is None


def test_qualified_cardinality_serialize() -> None:
    g1 = _setup_graph()
    g2 = _setup_graph()
    parent = Class(EX.Parent, graph=g1)
    r = Restriction(
        EX.hasChild,
        graph=g1,
        qualifiedCardinality=Literal(3, datatype=XSD.nonNegativeInteger),
        onClass=parent,
    )

    r.serialize(g2)

    assert (
        r.identifier,
        OWL.qualifiedCardinality,
        Literal(3, datatype=XSD.nonNegativeInteger),
    ) in g2
    assert (r.identifier, OWL.onClass, EX.Parent) in g2
    assert (r.identifier, OWL.onProperty, EX.hasChild) in g2
    assert (EX.Parent, RDF.type, OWL.Class) in g2


def test_qualified_cardinality_equality_and_hash() -> None:
    g = _setup_graph()
    count = Literal(3, datatype=XSD.nonNegativeInteger)
    r1 = Restriction(
        EX.hasChild, graph=g, qualifiedCardinality=count, onClass=EX.Parent
    )
    r2 = Restriction(
        EX.hasChild, graph=g, qualifiedCardinality=count, onClass=EX.Parent
    )
    r_max = Restriction(
        EX.hasChild, graph=g, maxQualifiedCardinality=count, onClass=EX.Parent
    )
    r_other_class = Restriction(
        EX.hasChild, graph=g, qualifiedCardinality=count, onClass=EX.Adult
    )
    r_unqualified = Restriction(EX.hasChild, graph=g, cardinality=count)

    assert r1 == r2
    assert hash(r1) == hash(r2)
    assert r1 != r_max
    assert r1 != r_other_class
    assert r1 != r_unqualified
    assert r1 != Class(EX.Parent, graph=g)
