"""
Unit tests for RDFS closure.
"""

from rdflib import RDF, XSD, Graph, Literal
from rdflib.plugins.inference import DeductiveClosure
from rdflib.plugins.inference.namespaces import T
from rdflib.plugins.inference.rdfsclosure import RDFS_Semantics


def test_one_time_rules():
    """
    Test RDFS closure one time rules.
    """
    g = Graph()

    lt1 = Literal(10, datatype=XSD.integer)
    lt2 = Literal(10, datatype=XSD.nonNegativeInteger)
    g.add((T.a1, T.p, lt1))
    g.add((T.a2, T.p, lt2))

    DeductiveClosure(RDFS_Semantics).expand(g)

    assert (T.a1, T.p, lt2) in g
    assert (T.a2, T.p, lt1) in g


def test_d_axioms():
    """
    Test adding datatype axioms for RDFS closure.
    """
    g = Graph()

    g.add((T.a1, T.p, Literal(10, datatype=XSD.integer)))
    g.add((T.a2, T.p, Literal("11", datatype=XSD.string)))
    g.add((T.a3, T.p, Literal("t")))  # no datatype

    DeductiveClosure(RDFS_Semantics, datatype_axioms=True).expand(g)

    assert (Literal(10, datatype=XSD.integer), RDF.type, XSD.integer) in g
    assert (Literal("11", datatype=XSD.string), RDF.type, XSD.string) in g
    assert next(g.subjects(Literal("t"), RDF.type), None) is None
